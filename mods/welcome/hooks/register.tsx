import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Art } from './card-types'
import { CARDS } from './cards'

const hasGreeted = atom({ plugin: 'welcome', key: 'hasGreeted' } as const, false)

const GAP = 3
const MIN_TEXT_COLUMNS = 20

export const register: Register = (on, options) => {
  const card = CARDS[String(options.theme)]
  if (card === undefined) {
    return
  }

  // The band gets at most half the terminal, shared with the prompt and the status line,
  // so the card draws the largest art that fits rather than none.
  const largestFitting = (maxRows: number, bodyColumns: number): Art | undefined =>
    card.sizes.find(art => art.rows.length <= maxRows && art.width + GAP + MIN_TEXT_COLUMNS <= bodyColumns)

  on('session.start', async ($, e, next) => {
    await update($, hasGreeted, () => false)
    return next(e)
  })

  // A failed write must never hold back the person's message.
  on('prompt.submit', async ($, e, next) => {
    await update($, hasGreeted, () => true)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const { hasSurvey, isWorking, bodyColumns, maxRows } = e.props
    const art = largestFitting(maxRows, bodyColumns)
    if (hasSurvey || isWorking || art === undefined || (await read($, hasGreeted))) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Box flexDirection="column">
          {art.rows.map((row, y) => (
            <Box key={`row-${y}`}>
              {row.map((run, x) => (
                <Text key={`run-${x}`} color={run.fg ?? undefined} backgroundColor={run.bg ?? undefined}>
                  {run.text}
                </Text>
              ))}
            </Box>
          ))}
        </Box>
        <Box flexDirection="column" justifyContent="center" marginLeft={GAP}>
          <Text color={card.caption}>{card.tagline}</Text>
        </Box>
      </Box>
    )
  })
}
