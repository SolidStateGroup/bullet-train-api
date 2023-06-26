import {
  Modal as _Modal,
  ModalBody as _ModalBody,
  ModalFooter as _ModalFooter,
  ModalHeader as _ModalHeader,
  ModalProps,
} from 'reactstrap'
import { JSXElementConstructor, ReactNode, useCallback, useState } from 'react'
import { render, unmountComponentAtNode } from 'react-dom'
import Confirm from './ModalConfirm'
import ModalDefault, { interceptClose } from './ModalDefault'
import Alert from './ModalAlert'
import { getStore } from 'common/store'
import { Provider } from 'react-redux'

export const ModalHeader = _ModalHeader
export const ModalFooter = _ModalFooter
export const Modal = _Modal
export const ModalBody = _ModalBody

const withModal = (
  WrappedComponent: JSXElementConstructor<any>,
  closePointer = 'closeModal',
  shouldInterceptClose = false,
) => {
  return (props: ModalProps) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [isOpen, setIsOpen] = useState(true)
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const toggle = useCallback(() => {
      if (interceptClose && shouldInterceptClose) {
        interceptClose().then(() => {
          setIsOpen(false)
        })
      } else {
        setIsOpen(false)
      }
    }, [setIsOpen])
    // @ts-ignore
    global[closePointer] = toggle

    return (
      <Provider store={getStore()}>
        <WrappedComponent toggle={toggle} {...props} isOpen={isOpen} />
      </Provider>
    )
  }
}

const _Confirm = withModal(Confirm)
const _ModalDefault2 = withModal(ModalDefault, 'closeModal2')
const _ModalDefault = withModal(ModalDefault, 'closeModal', true)

export const openConfirm = (global.openConfirm = (
  title: string,
  body: ReactNode,
  onYes?: () => void,
  onNo?: () => void,
) => {
  document.getElementById('confirm') &&
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    unmountComponentAtNode(document.getElementById('confirm')!)
  render(
    <_Confirm zIndex={1052} isOpen onNo={onNo} onYes={onYes} title={title}>
      {body}
    </_Confirm>,
    document.getElementById('confirm'),
  )
})

export const openModal = (global.openModal = (
  title: string,
  body: ReactNode,
  className?: string,
  onClose?: () => void,
) => {
  document.getElementById('modal') &&
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    unmountComponentAtNode(document.getElementById('modal')!)
  render(
    <_ModalDefault
      isOpen
      className={className}
      onClosed={onClose}
      title={title}
      zIndex={1050}
    >
      {body}
    </_ModalDefault>,
    document.getElementById('modal'),
  )
})

//This is used when we show modals on top of modals, the UI pattern should be avoided if possible
export const openModal2 = (global.openModal2 = (
  title: string,
  body: ReactNode,
  className?: string,
  onClose?: () => void,
) => {
  document.getElementById('modal2') &&
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    unmountComponentAtNode(document.getElementById('modal2')!)
  render(
    <_ModalDefault2
      isOpen
      className={className}
      onClosed={onClose}
      title={title}
      zIndex={1051}
    >
      {body}
    </_ModalDefault2>,
    document.getElementById('modal2'),
  )
})
