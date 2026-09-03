import { SECTIONS, isLeaf, sectionProgress } from '../../utils/draftFields.js'
import { customChildrenFor } from '../../utils/customSectionTree.js'
import SectionRow from './SectionRow.jsx'
import CustomSectionRow from './CustomSectionRow.jsx'

export default function SectionTree({
  answers,
  focusedFieldId,
  onFocus,
  customSections,
  onRenameCustomNode,
  onRemoveCustomNode,
  canEdit = true,
}) {
  return (
    <div className="px-7 pt-2 pb-7 flex flex-col gap-5">
      {SECTIONS.map((section) => {
        const { done, total } = sectionProgress(section.id, answers)
        const pct = total ? Math.round((done / total) * 100) : 0
        return (
          <div key={section.id}>
            <div className="flex items-center justify-between gap-2.5 py-3 pb-2 border-b border-border-light">
              <div className="flex items-center gap-2.5">
                <div
                  className="relative w-6.5 h-6.5 rounded-full flex-shrink-0"
                  style={{ background: `conic-gradient(#222222 0% ${pct}%, #f2f2f2 ${pct}% 100%)` }}
                >
                  <div className="absolute inset-1 bg-white rounded-full" />
                </div>
                <span className="text-[13px] font-semibold text-[#3f3f3f]">{section.title}</span>
              </div>
              <span className="text-xs text-text-tertiary">
                {done} / {total}
              </span>
            </div>
            <div className="flex flex-col">
              {section.children.map((node) =>
                isLeaf(node) ? (
                  <SectionRow
                    key={node.id}
                    leaf={{ ...node, dependsOn: node.dependsOn || [] }}
                    answers={answers}
                    focusedFieldId={focusedFieldId}
                    onFocus={onFocus}
                    grouped={false}
                  />
                ) : (
                  <div key={node.id}>
                    <div className="flex items-center gap-1.5 mt-2.5 py-1.5 pl-1">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#929292" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
                        <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                      </svg>
                      <span className="text-xs font-bold text-[#3f3f3f] uppercase tracking-wide">
                        {node.id} {node.title}
                      </span>
                    </div>
                    {node.children.map((leaf) => (
                      <SectionRow
                        key={leaf.id}
                        leaf={{ ...leaf, dependsOn: leaf.dependsOn || [] }}
                        answers={answers}
                        focusedFieldId={focusedFieldId}
                        onFocus={onFocus}
                        grouped
                      />
                    ))}
                    {customChildrenFor(customSections, node.id).map(({ node: cs, code }) => (
                      <CustomSectionRow
                        key={cs.id}
                        node={cs}
                        code={code}
                        onRename={onRenameCustomNode}
                        onRemove={onRemoveCustomNode}
                        answers={answers}
                        focusedFieldId={focusedFieldId}
                        onFocus={onFocus}
                        indent
                        canEdit={canEdit}
                      />
                    ))}
                  </div>
                ),
              )}
              {customChildrenFor(customSections, section.id).map(({ node: cs, code }) => (
                <CustomSectionRow
                  key={cs.id}
                  node={cs}
                  code={code}
                  onRename={onRenameCustomNode}
                  onRemove={onRemoveCustomNode}
                  answers={answers}
                  focusedFieldId={focusedFieldId}
                  onFocus={onFocus}
                  canEdit={canEdit}
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
