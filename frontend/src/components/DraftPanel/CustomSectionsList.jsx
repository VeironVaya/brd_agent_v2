import CustomSectionRow from './CustomSectionRow.jsx'
import { standaloneCustomSections } from '../../utils/customSectionTree.js'

/** Renders only the standalone (nestUnder: null) top-level custom sections — nested-under-template ones render inline in SectionTree. */
export default function CustomSectionsList({
  customSections,
  onRenameNode,
  onRemoveNode,
  onAddClick,
  answers,
  focusedFieldId,
  onFocus,
  onViewAnswer,
  canEdit = true,
}) {
  const standalone = standaloneCustomSections(customSections)

  return (
    <div>
      <div className="flex items-center justify-between py-3 pb-2 border-b border-border-light">
        <span className="text-[13px] font-semibold text-[#3f3f3f]">Custom Sections</span>
      </div>
      <div className="flex flex-col">
        {standalone.map(({ node, code }) => (
          <CustomSectionRow
            key={node.id}
            node={node}
            code={code}
            onRename={onRenameNode}
            onRemove={onRemoveNode}
            answers={answers}
            focusedFieldId={focusedFieldId}
            onFocus={onFocus}
            onViewAnswer={onViewAnswer}
            canEdit={canEdit}
          />
        ))}
        {canEdit && (
          <div
            onClick={onAddClick}
            className="mt-2 border-[1.5px] border-dashed border-border rounded-btn px-3.5 py-3 text-[13px] text-text-tertiary text-center cursor-pointer hover:border-text-primary hover:text-[#3f3f3f]"
          >
            + Add custom section
          </div>
        )}
      </div>
    </div>
  )
}
