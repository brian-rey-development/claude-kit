import { expect, test } from 'claude-code/testing'

import { CARDS } from '../hooks/cards'

const THEME = 'moonlit'
const SURFACES = ['terminal', 'desktop'] as const
const idle = { hasSurvey: false, isWorking: false, maxRows: 40, bodyColumns: 100, scroll: { offset: 0, bodyRows: 39 }, view: {} }
const card = CARDS[THEME]

test('the card draws the art and the tagline before the first prompt', { options: { theme: THEME } }, async $ => {
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ plugin: 'welcome', surface, component: 'AbovePrompt', props: idle })
    expect(await ui.find({ type: 'Text', text: card.tagline })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /█|▀|▄/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a short band gets a smaller art instead of no card', { options: { theme: THEME } }, async $ => {
  const smallest = card.sizes.at(-1)
  if (smallest === undefined) throw new Error(`${THEME} has no card art`)
  const props = { ...idle, maxRows: smallest.rows.length }
  const ui = await $.ui.mount({ plugin: 'welcome', surface: 'terminal', component: 'AbovePrompt', props })
  expect(await ui.find({ type: 'Text', text: card.tagline })).toBeDefined()
  await ui.unmount()
})

test('the card steps aside while a turn runs or the band is too narrow', { options: { theme: THEME } }, async ($, on) => {
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine band</Text>
  })
  for (const props of [{ ...idle, isWorking: true }, { ...idle, bodyColumns: 20 }]) {
    const ui = await $.ui.mount({ plugin: 'welcome', surface: 'terminal', component: 'AbovePrompt', props })
    expect(await ui.find({ type: 'Text', text: card.tagline })).toBeUndefined()
    await ui.unmount()
  }
})

test('an unknown theme draws no card', { options: { theme: 'missing' } }, async ($, on) => {
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine band</Text>
  })
  const ui = await $.ui.mount({ plugin: 'welcome', surface: 'terminal', component: 'AbovePrompt', props: idle })
  expect(await ui.find({ type: 'Text', text: 'engine band' })).toBeDefined()
  await ui.unmount()
})
