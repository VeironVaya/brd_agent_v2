import { BOILERPLATE_SECTIONS } from '../../utils/draftFields.js'

export default function BoilerplateSection() {
  const section = BOILERPLATE_SECTIONS[0]
  return (
    <div>
      <div className="flex items-center justify-between py-3 pb-2 border-b border-border-light">
        <span className="text-[13px] font-semibold text-[#3f3f3f]">{section.title}</span>
        <span className="text-[11px] font-semibold text-text-tertiary bg-bg-subtlest rounded-pill px-2.5 py-0.75">
          Boilerplate
        </span>
      </div>
      <div className="py-2.25 text-[13px] text-text-tertiary">{section.description}</div>
    </div>
  )
}
