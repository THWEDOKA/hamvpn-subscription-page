import { Box, Card, Group, Stack, Text, Title } from '@mantine/core'

import { getLocalizedText } from '@shared/utils/config-parser'

import { IBlockRendererProps } from '../renderer-block.interface'
import classes from './cards-block.module.css'

export const CardsBlockRenderer = ({
    blocks,
    isMobile,
    currentLang,
    renderBlockButtons
}: IBlockRendererProps) => {
    return (
        <Stack gap="sm">
            {blocks.map((block, index) => {
                return (
                    <Card
                        className={classes.root}
                        key={index}
                        p={{ base: 'sm', xs: 'md', sm: 'lg' }}
                        radius="lg"
                    >
                        <Group align="flex-start" gap={isMobile ? 'sm' : 'md'} wrap="nowrap">
                            <Box className={classes.stepNumber}>{index + 1}</Box>
                            <Stack gap={isMobile ? 'xs' : 'sm'} style={{ flex: 1, minWidth: 0 }}>
                                <Text className={classes.stepMeta} fw={700} size="xs">
                                    {currentLang === 'ru'
                                        ? `ШАГ ${index + 1}`
                                        : `STEP ${index + 1}`}
                                </Text>
                                <Title
                                    c="white"
                                    fw={600}
                                    order={6}
                                    style={{ wordBreak: 'break-word' }}
                                >
                                    <span
                                        dangerouslySetInnerHTML={{
                                            __html: getLocalizedText(block.title, currentLang)
                                        }}
                                    />
                                </Title>

                                <Text
                                    size={isMobile ? 'xs' : 'sm'}
                                    style={{ whiteSpace: 'pre-line', lineHeight: 1.6 }}
                                >
                                    <span
                                        dangerouslySetInnerHTML={{
                                            __html: getLocalizedText(block.description, currentLang)
                                        }}
                                    />
                                </Text>

                                {renderBlockButtons(block.buttons, 'light')}
                            </Stack>
                        </Group>
                    </Card>
                )
            })}
        </Stack>
    )
}
