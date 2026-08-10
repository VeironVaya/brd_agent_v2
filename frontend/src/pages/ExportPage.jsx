import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import * as api from '../services/api.js'
import { SECTIONS, isLeaf, overallProgress, flattenLeaves } from '../utils/draftFields.js'
import { customChildrenFor, standaloneCustomSections, findCustomNode, getCodeForNode } from '../utils/customSectionTree.js'
import Logo from '../components/common/Logo.jsx'
import Modal, { ModalHeader } from '../components/common/Modal.jsx'
import UserMenu from '../components/common/UserMenu.jsx'
import ConfirmModal from '../components/common/ConfirmModal.jsx'
import { downloadMarkdown, downloadPdf } from '../utils/documentPdf.js'

export default function ExportPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [conversation, setConversation] = useState(null)
  const [format, setFormat] = useState('pdf')
  const [phase, setPhase] = useState('idle') // idle | generating | success | error
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [activeResultId, setActiveResultId] = useState(null)
  const [result, setResult] = useState(null)
  const [logoutOpen, setLogoutOpen] = useState(false)

  useEffect(() => {
    api.getConversation(id).then(setConversation)
  }, [id])

  if (!conversation) {
    return <div className="w-full min-h-screen flex items-center justify-center text-text-secondary">Loading…</div>
  }

  const answers = conversation.answers
  const { done, total } = overallProgress(answers)
  const isComplete = done === total
  const sectionDescriptions = conversation.sectionDescriptions || {}

  async function runGenerate() {
    setPhase('generating')
    try {
      const res = await api.generateDocument(id, format)
      setResult(res)
      setPhase('success')
    } catch {
      setPhase('error')
    }
  }

  function handleGenerateClick() {
    if (!isComplete) {
      setConfirmOpen(true)
      return
    }
    runGenerate()
  }

  function handleDownload() {
    if (!result) return
    if (format === 'markdown') {
      downloadMarkdown(result.markdown, result.filename)
    } else {
      downloadPdf(result.markdown, result.filename)
    }
  }

  const activeTemplateLeaf = activeResultId ? flattenLeaves().find((n) => n.id === activeResultId) : null
  const activeCustomNode =
    !activeTemplateLeaf && activeResultId ? findCustomNode(conversation.customSections, activeResultId) : null
  const activeLeaf =
    activeTemplateLeaf || (activeCustomNode ? { id: activeCustomNode.id, title: activeCustomNode.title } : null)
  const activeCode = activeTemplateLeaf
    ? activeTemplateLeaf.id
    : activeCustomNode
      ? getCodeForNode(conversation.customSections, activeCustomNode.id)
      : null

  return (
    <div className="w-full min-h-screen bg-white">
      <div className="flex items-center gap-4 px-10 py-5 border-b border-divider flex-wrap">
        <Logo size={30} />
        <span className="w-px h-6.5 bg-border flex-shrink-0" />
        <button
          type="button"
          onClick={() => navigate(`/conversations/${id}`)}
          className="flex items-center gap-1.5 text-sm cursor-pointer flex-shrink-0 whitespace-nowrap"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="m12 19-7-7 7-7" />
          </svg>
          Workspace
        </button>
        <span className="w-px h-5.5 bg-border flex-shrink-0" />
        <div className="min-w-0">
          <div className="text-[21px] font-bold whitespace-nowrap overflow-hidden text-ellipsis">
            {conversation.title} — Export
          </div>
          <div className="text-[13px] text-text-secondary mt-0.5">
            {done} of 26 answered · {isComplete ? 'ready to generate' : 'incomplete'}
          </div>
        </div>
        <div className="ml-auto">
          <UserMenu onLogout={() => setLogoutOpen(true)} />
        </div>
      </div>

      {phase === 'idle' && (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_340px] gap-8 px-10 pt-8 pb-12 items-start">
          <div className="bg-bg-subtle rounded-2xl p-10 flex justify-center">
            <div className="w-full max-w-160 bg-white border border-border-light rounded-sm shadow-[0_8px_24px_rgba(0,0,0,.06)] px-12 py-14 flex flex-col gap-5.5">
              <div className="text-center pb-5 border-b border-border-light">
                <div className="text-xs font-semibold tracking-widest uppercase text-text-tertiary">
                  Business Requirement Document
                </div>
                <div className="text-2xl font-bold mt-2">{conversation.title}</div>
                <div className="text-[13px] text-text-tertiary mt-1.5">
                  {conversation.docVersion || 'Version 1.0'} · {conversation.docGeneratedLabel || 'Not yet generated'}
                </div>
              </div>

              {SECTIONS.map((section) => (
                <div key={section.id}>
                  <div className="mt-1.5">
                    <div className="text-[15px] font-bold">
                      {section.id}. {section.title}
                    </div>
                    <div className="text-[13.5px] text-[#3f3f3f] mt-1.5 leading-relaxed">
                      {sectionDescriptions[section.id] || 'Auto-generated summary of this section.'}
                    </div>
                  </div>
                  {section.children.map((node) =>
                    isLeaf(node) ? (
                      <ExportRow key={node.id} id={node.id} title={node.title} onView={setActiveResultId} />
                    ) : (
                      <div key={node.id}>
                        <div className="text-[12.5px] font-bold text-text-secondary mt-1">
                          {node.id} {node.title}
                        </div>
                        {node.children.map((leaf) => (
                          <ExportRow key={leaf.id} id={leaf.id} title={leaf.title} onView={setActiveResultId} />
                        ))}
                        {customChildrenFor(conversation.customSections, node.id).map(({ node: cs, code }) => (
                          <ExportCustomRow key={cs.id} node={cs} code={code} onView={setActiveResultId} />
                        ))}
                      </div>
                    ),
                  )}
                  {customChildrenFor(conversation.customSections, section.id).map(({ node: cs, code }) => (
                    <ExportCustomRow key={cs.id} node={cs} code={code} onView={setActiveResultId} />
                  ))}
                </div>
              ))}

              {standaloneCustomSections(conversation.customSections).length > 0 && (
                <div>
                  <div className="mt-1.5">
                    <div className="text-[15px] font-bold">Custom Sections</div>
                  </div>
                  {standaloneCustomSections(conversation.customSections).map(({ node: cs, code }) => (
                    <ExportCustomRow key={cs.id} node={cs} code={code} onView={setActiveResultId} />
                  ))}
                </div>
              )}

              <div className="mt-3 pt-5 border-t border-border-light text-xs text-[#c1c1c1] text-center">
                Page 1 of 14
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-5 xl:sticky xl:top-8">
            <div className="border border-border-light rounded-[14px] p-5.5">
              <div className="text-[15px] font-bold">Export as</div>
              <div className="flex flex-col gap-2 mt-3.5">
                <FormatOption
                  active={format === 'pdf'}
                  onClick={() => setFormat('pdf')}
                  label="PDF Document"
                  icon={
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  }
                  secondIcon={<path d="M14 2v6h6" />}
                />
                <FormatOption
                  active={format === 'markdown'}
                  onClick={() => setFormat('markdown')}
                  label="Markdown (.md)"
                  icon={<path d="M4 4h16v16H4z" />}
                  secondIcon={
                    <>
                      <path d="M7 15V9l3 3 3-3v6" />
                      <path d="m17 9-2.5 3L17 15" />
                    </>
                  }
                />
              </div>
              <button
                type="button"
                onClick={handleGenerateClick}
                className="flex items-center justify-center gap-2 w-full bg-accent text-white border-none rounded-btn h-12 text-[15px] font-semibold cursor-pointer mt-5"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3v13" />
                  <path d="m6 11 6 6 6-6" />
                  <path d="M4 21h16" />
                </svg>
                Generate BRD
              </button>
              <button
                type="button"
                onClick={() => {
                  api.setForceNextGenerateError(true)
                  handleGenerateClick()
                }}
                className="w-full text-center text-xs text-text-tertiary mt-3 cursor-pointer bg-transparent border-none"
              >
                Simulate a failed generation (dev)
              </button>
            </div>
          </div>
        </div>
      )}

      {phase === 'generating' && (
        <div className="flex flex-col items-center justify-center text-center py-30 px-10">
          <div className="w-12 h-12 rounded-full border-4 border-border-light border-t-text-primary animate-spin" />
          <div className="text-[19px] font-bold mt-6">Generating your BRD…</div>
          <div className="text-sm text-text-secondary mt-2">This usually takes a few seconds.</div>
        </div>
      )}

      {phase === 'success' && (
        <div className="flex flex-col items-center justify-center text-center py-25 px-10">
          <div className="w-16 h-16 rounded-full bg-[#e8f5e9] flex items-center justify-center">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#1a7f37" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
          <div className="text-[19px] font-bold mt-5">BRD generated</div>
          <div className="text-sm text-text-secondary mt-2">{result?.filename} is ready.</div>
          <div className="flex gap-2.5 mt-6">
            <button
              type="button"
              onClick={handleDownload}
              className="flex items-center gap-2 bg-accent text-white border-none rounded-btn h-12 px-6 text-[15px] font-semibold cursor-pointer"
            >
              Download
            </button>
            <button
              type="button"
              onClick={() => navigate(`/conversations/${id}`)}
              className="flex items-center gap-2 bg-white text-text-primary border border-text-primary rounded-btn h-12 px-6 text-[15px] font-semibold cursor-pointer"
            >
              Back to Workspace
            </button>
          </div>
        </div>
      )}

      {phase === 'error' && (
        <div className="flex flex-col items-center justify-center text-center py-25 px-10">
          <div className="w-16 h-16 rounded-full bg-[#fdecea] flex items-center justify-center">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#c13515" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </div>
          <div className="text-[19px] font-bold mt-5">Something went wrong</div>
          <div className="text-sm text-text-secondary mt-2 max-w-85">
            We couldn't generate this document. Please try again.
          </div>
          <div className="flex gap-2.5 mt-6">
            <button
              type="button"
              onClick={runGenerate}
              className="bg-accent text-white border-none rounded-btn h-12 px-6 text-[15px] font-semibold cursor-pointer"
            >
              Try Again
            </button>
            <button
              type="button"
              onClick={() => navigate(`/conversations/${id}`)}
              className="flex items-center gap-2 bg-white text-text-primary border border-text-primary rounded-btn h-12 px-6 text-[15px] font-semibold cursor-pointer"
            >
              Back to Workspace
            </button>
          </div>
        </div>
      )}

      <Modal open={confirmOpen} onClose={() => setConfirmOpen(false)} maxWidth={420} zIndex={20}>
        <span className="text-[17px] font-bold">Are you sure?</span>
        <div className="text-[13.5px] text-text-secondary mt-2 leading-relaxed">
          This BRD isn't complete yet — some sections still have open items. Generating now will
          leave gaps in the document.
        </div>
        <div className="flex justify-end gap-2.5 mt-5.5">
          <button
            type="button"
            onClick={() => setConfirmOpen(false)}
            className="bg-white text-text-primary border border-border rounded-btn h-10.5 px-4.5 text-sm font-semibold cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              setConfirmOpen(false)
              runGenerate()
            }}
            className="bg-accent text-white border-none rounded-btn h-10.5 px-5 text-sm font-semibold cursor-pointer"
          >
            Generate Anyway
          </button>
        </div>
      </Modal>

      <Modal open={!!activeResultId} onClose={() => setActiveResultId(null)}>
        {activeLeaf && (
          <>
            <ModalHeader title={`${activeCode} ${activeLeaf.title}`} onClose={() => setActiveResultId(null)} size="sm" />
            <div className="text-sm mt-4 leading-relaxed">
              {answers[activeLeaf.id]?.answer || 'No answer recorded yet.'}
            </div>
            <div className="flex justify-end mt-5.5">
              <button
                type="button"
                onClick={() => setActiveResultId(null)}
                className="bg-text-primary text-white border-none rounded-btn h-10 px-5 text-[13px] font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </>
        )}
      </Modal>

      <ConfirmModal
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        onConfirm={() => {
          api.logout()
          navigate('/login')
        }}
        title="Log out?"
        description="You'll be signed out of BRD-Agent and returned to the sign-in screen."
        confirmLabel="Log out"
      />
    </div>
  )
}

function ExportRow({ id, code, title, onView }) {
  return (
    <div className="flex items-baseline justify-between gap-2.5 py-0.75">
      <span className="text-[13px] text-[#3f3f3f]">
        {code ?? id} {title}
      </span>
      <button
        type="button"
        onClick={() => onView(id)}
        className="bg-transparent border-none text-text-primary text-xs font-semibold underline cursor-pointer flex-shrink-0"
      >
        View
      </button>
    </div>
  )
}

/** Recursive — a custom group renders as a sub-header (like a template's 3.3-style node), a leaf renders like ExportRow. */
function ExportCustomRow({ node, code, onView }) {
  if (node.hasChildren) {
    return (
      <div>
        <div className="text-[12.5px] font-bold text-text-secondary mt-1">
          {code} {node.title}
        </div>
        {node.children.map((child, i) => (
          <ExportCustomRow key={child.id} node={child} code={`${code}.${i + 1}`} onView={onView} />
        ))}
      </div>
    )
  }
  return <ExportRow id={node.id} code={code} title={node.title} onView={onView} />
}

function FormatOption({ active, onClick, label, icon, secondIcon }) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center justify-between gap-2.5 rounded-[10px] px-3.5 py-3 cursor-pointer ${
        active ? 'border-[1.5px] border-text-primary bg-bg-subtler' : 'border border-border'
      }`}
    >
      <div className="flex items-center gap-2.5">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? '#222222' : '#6a6a6a'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          {icon}
          {secondIcon}
        </svg>
        <span className={`text-sm ${active ? 'font-semibold text-text-primary' : 'font-medium text-[#3f3f3f]'}`}>
          {label}
        </span>
      </div>
      {active ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="12" fill="#222222" />
          <path d="M7 12.5l3 3 7-7" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dddddd" strokeWidth="1.8">
          <circle cx="12" cy="12" r="9" />
        </svg>
      )}
    </div>
  )
}
