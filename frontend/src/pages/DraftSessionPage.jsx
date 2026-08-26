import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'
import * as api from '../services/api.js'
import {
  GENERAL_ROOM_ID,
  FIELD_META,
  FIELD_ORDER,
  fieldState,
  missingByStatus,
  statusBuckets,
  overallProgress,
} from '../utils/draftFields.js'
import { buildNote } from '../components/DraftPanel/SectionRow.jsx'
import { findCustomNode, getCodeForNode } from '../utils/customSectionTree.js'
import { isChoiceSection } from '../utils/choiceSections.js'

import ChatHeader from '../components/Chat/ChatHeader.jsx'
import FocusBar from '../components/Chat/FocusBar.jsx'
import MessageThread from '../components/Chat/MessageThread.jsx'
import MessageInput from '../components/Chat/MessageInput.jsx'

import ProgressHeader from '../components/DraftPanel/ProgressHeader.jsx'
import SectionTree from '../components/DraftPanel/SectionTree.jsx'
import BoilerplateSection from '../components/DraftPanel/BoilerplateSection.jsx'
import CustomSectionsList from '../components/DraftPanel/CustomSectionsList.jsx'
import AddCustomSectionModal from '../components/DraftPanel/AddCustomSectionModal.jsx'
import ReviewFlaggedModal from '../components/DraftPanel/ReviewFlaggedModal.jsx'
import AnswerDetailModal from '../components/DraftPanel/AnswerDetailModal.jsx'
import SectionCompleteModal from '../components/DraftPanel/SectionCompleteModal.jsx'
import ConfirmModal from '../components/common/ConfirmModal.jsx'
import ShareModal from '../components/common/ShareModal.jsx'
import ChoiceSectionModal from '../components/ChoiceSections/ChoiceSectionModal.jsx'

export default function DraftSessionPage() {
  const { id } = useParams()
  const { logout } = useAuth()
  const [conversation, setConversation] = useState(null)
  const [loading, setLoading] = useState(true)

  const [focusedFieldId, setFocusedFieldId] = useState(null)
  const [roomTab, setRoomTab] = useState('question')
  const [aiModel, setAiModel] = useState('Local')

  const [reviewOpen, setReviewOpen] = useState(false)
  const [addSectionOpen, setAddSectionOpen] = useState(false)
  const [viewAnswerFieldId, setViewAnswerFieldId] = useState(null)
  const [logoutOpen, setLogoutOpen] = useState(false)
  const [shareOpen, setShareOpen] = useState(false)
  const [choiceSectionId, setChoiceSectionId] = useState(null)
  // { completedTitle, nextFieldId, nextTitle } | null
  // Populated after the AI marks the focused section as 'done' so the
  // SectionCompleteModal can offer a one-click jump to the next section.
  const [sectionCompleteData, setSectionCompleteData] = useState(null)
  // Optimistic send: the user's own message renders immediately, with a
  // "thinking" indicator in place of the agent's reply, rather than
  // blocking on the full round trip — matters once the AI stub is a real,
  // slower model. Scoped to a room id so switching rooms mid-send doesn't
  // show a stale indicator in the wrong thread.
  const [pending, setPending] = useState(null) // { roomId, text } | null

  useEffect(() => {
    let active = true
    setLoading(true)
    api.getConversation(id).then((detail) => {
      if (!active) return
      setConversation(detail)
      const focusedId = detail.focusedFieldId || null
      setFocusedFieldId(focusedId)
      // A brand-new conversation has nothing focused yet — land on General
      // chat, which is always usable, instead of defaulting to "This
      // question" with a disabled input and nothing to discuss. Once
      // something's been discussed before, keep returning to that focus.
      setRoomTab(focusedId ? 'question' : 'general')
      setLoading(false)
    })
    return () => {
      active = false
    }
  }, [id])

  if (loading || !conversation) {
    return <div className="w-full min-h-screen flex items-center justify-center text-text-secondary">Loading…</div>
  }

  const answers = conversation.answers
  const percent = Math.round((overallProgress(answers).done / 26) * 100)
  const buckets = statusBuckets(answers)
  // "owner"/"editor" can chat and edit sections; "viewer" is read + export only.
  const canEdit = conversation.role === 'owner' || conversation.role === 'editor'

  const roomId = roomTab === 'question' ? focusedFieldId : GENERAL_ROOM_ID
  const isSending = pending?.roomId === roomId
  const messages = isSending
    ? [...(conversation.messages[roomId] || []), { id: '__pending__', role: 'user', text: pending.text }]
    : conversation.messages[roomId] || []
  const focusedTemplateLeaf = focusedFieldId ? FIELD_META[focusedFieldId] : null
  const focusedCustomNode =
    !focusedTemplateLeaf && focusedFieldId ? findCustomNode(conversation.customSections, focusedFieldId) : null
  const focusedLeaf =
    focusedTemplateLeaf ||
    (focusedCustomNode
      ? {
          id: focusedCustomNode.id,
          code: getCodeForNode(conversation.customSections, focusedCustomNode.id),
          title: focusedCustomNode.title,
        }
      : null)
  const focusedCode = focusedLeaf ? (focusedLeaf.code ?? focusedLeaf.id) : null
  const focusedStatus = focusedFieldId ? fieldState(focusedFieldId, answers) : null
  const placeholderText =
    roomTab === 'question' && !focusedLeaf
      ? 'Pick a question from the panel on the right to start discussing it here — or switch to General chat to talk freely in the meantime.'
      : focusedLeaf && messages.length === 0 && roomTab === 'question'
        ? missingByStatus(focusedStatus, buildNote(focusedLeaf, answers))
        : "Ask me anything about this BRD, or pick a question from the panel on the right."

  async function refreshDetail() {
    const detail = await api.getConversation(id)
    setConversation(detail)
  }

  async function handleSend(text) {
    // Hard guard, not just the input's `disabled` prop — a fast double
    // click/double-Enter can otherwise fire two real POSTs before React
    // re-renders the disabled state, producing two user+agent pairs for
    // one send.
    if (isSending || !canEdit) return

    // Capture the focused field's status before the round-trip so we can
    // detect the moment the AI flips it to 'done'.
    const prevStatus = focusedFieldId ? fieldState(focusedFieldId, conversation.answers) : null

    setPending({ roomId, text })
    try {
      await api.postMessage(id, roomId, text)
      const detail = await api.getConversation(id)
      setConversation(detail)

      // Show the section-complete modal only when:
      //   • we were focused on a question room (not General)
      //   • the section wasn't already 'done' before this send
      //   • the AI just marked it 'done'
      if (
        roomTab === 'question' &&
        focusedFieldId &&
        prevStatus !== 'done' &&
        fieldState(focusedFieldId, detail.answers) === 'done'
      ) {
        const completedMeta = FIELD_META[focusedFieldId]
        const completedTitle = completedMeta?.title ?? focusedFieldId

        // Find the next leaf that is not done and not locked.
        const nextFieldId = FIELD_ORDER.find(
          (fid) =>
            fid !== focusedFieldId &&
            fieldState(fid, detail.answers) !== 'done' &&
            fieldState(fid, detail.answers) !== 'locked',
        ) ?? null
        const nextTitle = nextFieldId ? (FIELD_META[nextFieldId]?.title ?? nextFieldId) : null

        setSectionCompleteData({ completedTitle, nextFieldId, nextTitle })
      }
    } finally {
      setPending(null)
    }
  }

  async function handleCreateCustomSection(target, payload) {
    const created = await api.addCustomSectionNode(id, target, payload)
    await refreshDetail()
    return created
  }

  function handleFocus(fieldId) {
    setFocusedFieldId(fieldId)
    setRoomTab('question')
    if (canEdit && isChoiceSection(fieldId)) setChoiceSectionId(fieldId)
  }

  async function handleSaveChoices(choiceData) {
    await api.saveChoices(id, choiceSectionId, choiceData)
    await refreshDetail()
  }

  async function handleRenameCustomNode(nodeId, title) {
    await api.renameCustomSectionNode(id, nodeId, title)
    await refreshDetail()
  }

  async function handleRemoveCustomNode(nodeId) {
    await api.removeCustomSectionNode(id, nodeId)
    await refreshDetail()
  }

  function handleResolveInChat(fieldId) {
    setFocusedFieldId(fieldId)
    setRoomTab('question')
    setReviewOpen(false)
  }

  return (
    <div className="w-full h-screen bg-white flex flex-col overflow-hidden">
      <div className="flex-shrink-0">
        <ChatHeader
          conversation={{ ...conversation, id }}
          aiModel={aiModel}
          onToggleModel={() => setAiModel((m) => (m === 'Local' ? 'Cloud' : 'Local'))}
          flaggedCount={conversation.flaggedItems.length}
          onOpenReview={() => setReviewOpen(true)}
          onOpenShare={() => setShareOpen(true)}
          onLogout={() => setLogoutOpen(true)}
        />
      </div>

      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[minmax(0,1.4fr)_minmax(320px,440px)]">
        <div className="bg-bg-subtle flex flex-col min-w-0 min-h-0">
          <div className="flex-shrink-0">
            <FocusBar
              focusedLabel={focusedLeaf ? `${focusedCode} ${focusedLeaf.title}` : '—'}
              roomTab={roomTab}
              onChangeRoomTab={setRoomTab}
              onOpenChoices={focusedFieldId && canEdit && isChoiceSection(focusedFieldId)
                ? () => setChoiceSectionId(focusedFieldId)
                : null}
            />
          </div>
          <MessageThread messages={messages} placeholderText={placeholderText} thinking={isSending} />
          <div className="flex-shrink-0">
            <MessageInput
              onSend={handleSend}
              disabled={(!focusedFieldId && roomTab === 'question') || isSending || !canEdit}
            />
          </div>
        </div>

        <div className="bg-white flex flex-col min-w-0 min-h-0 border-l border-divider">
          <div className="flex-shrink-0">
            <ProgressHeader percent={percent} buckets={buckets} />
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto">
            <SectionTree
              answers={answers}
              focusedFieldId={focusedFieldId}
              onFocus={(fieldId) => {
                handleFocus(fieldId)
              }}
              onViewAnswer={setViewAnswerFieldId}
              customSections={conversation.customSections}
              onRenameCustomNode={handleRenameCustomNode}
              onRemoveCustomNode={handleRemoveCustomNode}
              canEdit={canEdit}
            />
            <div className="px-7 pb-7 flex flex-col gap-5">
              <BoilerplateSection />
              <CustomSectionsList
                customSections={conversation.customSections}
                onRenameNode={handleRenameCustomNode}
                onRemoveNode={handleRemoveCustomNode}
                onAddClick={() => setAddSectionOpen(true)}
                answers={answers}
                focusedFieldId={focusedFieldId}
                onFocus={(fieldId) => {
                  handleFocus(fieldId)
                }}
                onViewAnswer={setViewAnswerFieldId}
                canEdit={canEdit}
              />
            </div>
          </div>
        </div>
      </div>

      <AddCustomSectionModal
        open={addSectionOpen}
        onClose={() => setAddSectionOpen(false)}
        onCreate={handleCreateCustomSection}
        customSections={conversation.customSections}
      />
      <ReviewFlaggedModal
        open={reviewOpen}
        onClose={() => setReviewOpen(false)}
        flaggedItems={conversation.flaggedItems}
        answers={answers}
        onRecompute={() => api.recomputeReview(id)}
        onResolveInChat={handleResolveInChat}
      />
      <AnswerDetailModal
        open={!!viewAnswerFieldId}
        onClose={() => setViewAnswerFieldId(null)}
        fieldId={viewAnswerFieldId}
        answers={answers}
        customSections={conversation.customSections}
      />
      <ConfirmModal
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        onConfirm={async () => {
          setLogoutOpen(false)
          await logout() // awaits server revocation + clears state + navigates to /login
        }}
        title="Log out?"
        description="You'll be signed out of BRD-Agent and returned to the sign-in screen."
        confirmLabel="Log out"
      />
      <ShareModal open={shareOpen} onClose={() => setShareOpen(false)} conversationId={id} />
      <SectionCompleteModal
        open={!!sectionCompleteData}
        completedTitle={sectionCompleteData?.completedTitle ?? ''}
        nextTitle={sectionCompleteData?.nextTitle ?? null}
        onProceed={() => {
          if (sectionCompleteData?.nextFieldId) handleFocus(sectionCompleteData.nextFieldId)
          setSectionCompleteData(null)
        }}
        onStay={() => setSectionCompleteData(null)}
      />
      <ChoiceSectionModal
        open={!!choiceSectionId}
        sectionId={choiceSectionId}
        answer={choiceSectionId ? answers[choiceSectionId] : null}
        onClose={() => setChoiceSectionId(null)}
        onDiscuss={() => {
          setChoiceSectionId(null)
          setRoomTab('question')
        }}
        onSave={handleSaveChoices}
      />
    </div>
  )
}
