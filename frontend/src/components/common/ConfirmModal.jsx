import Modal from './Modal.jsx'
import Button from './Button.jsx'

export default function ConfirmModal({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
}) {
  return (
    <Modal open={open} onClose={onClose} maxWidth={420} zIndex={30}>
      <span className="text-[17px] font-bold">{title}</span>
      <div className="text-[13.5px] text-text-secondary mt-2 leading-relaxed">{description}</div>
      <div className="flex justify-end gap-2.5 mt-5.5">
        <Button variant="secondary" size="sm" onClick={onClose}>
          {cancelLabel}
        </Button>
        <Button variant="primary" size="sm" onClick={onConfirm}>
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  )
}
