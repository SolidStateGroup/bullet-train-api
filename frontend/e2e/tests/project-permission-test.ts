import {
  byId,
  click,
  createFeature,
  gotoSegments,
  log,
  login,
  setText,
  toggleFeature,
  waitForElementVisible,
} from '../helpers.cafe'
import {
  PASSWORD,
  E2E_NON_ADMIN_USER_WITH_PROJECT_PERMISSIONS,
} from '../config'
import { Selector, t } from 'testcafe'

export default async function () {
  log('Login')
  await login(E2E_NON_ADMIN_USER_WITH_PROJECT_PERMISSIONS, PASSWORD)
  log('User only can see an project')
  await click('#project-select-0')
  await t
    .expect(Selector('#project-select-1').exists)
    .notOk('The element"#project-select-1" should not be present')
  log('User with permissions can create an environment')
  await setText('[name="envName"]', 'Staging')
  await click('#create-env-btn')
  await waitForElementVisible(byId('switch-environment-staging-active'))
  log('User with permissions can Handle the Features')
  await createFeature(0, 'test_feature', false)
  await toggleFeature(0, true)
  await t.eval(() => {
    window.scrollBy(0, 15000)
  })
  log('User without permissions cannot Delete any feature')
  await click(byId('feature-action-0'))
  await waitForElementVisible(byId('remove-feature-btn-0'))
  await click(byId('remove-feature-btn-0'))
  await Selector(byId('remove-feature-btn-0')).hasClass(
    'feature-action__item_disabled',
  )
  log('User without permissions cannot Manage Segments')
  await gotoSegments()
  const createSegmentBtn = Selector(byId('show-create-segment-btn'))
  await t.expect(createSegmentBtn.hasAttribute('disabled')).ok()
  log('User with permissions can see the Audit Logs')
  await click(byId('audit-log-link'))
}
