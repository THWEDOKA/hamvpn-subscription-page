import { Box, Center, Container, Group, Image, Stack, Text, Title } from '@mantine/core'
import { TSubscriptionPagePlatformKey } from '@remnawave/subscription-page-types'
import {
    AccordionBlockRenderer,
    CardsBlockRenderer,
    InstallationGuideConnector,
    MinimalBlockRenderer,
    RawKeysWidget,
    SubscriptionInfoCardsWidget,
    SubscriptionInfoCollapsedWidget,
    SubscriptionInfoExpandedWidget,
    SubscriptionLinkWidget,
    TimelineBlockRenderer
} from '@widgets/main'

import { Page } from '@shared/ui'
import { LanguagePicker } from '@shared/ui/language-picker/language-picker.shared'

import { useAppConfig, useAppConfigStoreActions, useCurrentLang } from '@entities/app-config-store'

import classes from './main.page.module.css'

interface IMainPageComponentProps {
    isMobile: boolean
    platform: TSubscriptionPagePlatformKey | undefined
}

const BLOCK_RENDERERS = {
    cards: CardsBlockRenderer,
    timeline: TimelineBlockRenderer,
    accordion: AccordionBlockRenderer,
    minimal: MinimalBlockRenderer
} as const

const SUBSCRIPTION_INFO_BLOCK_RENDERERS = {
    cards: SubscriptionInfoCardsWidget,
    collapsed: SubscriptionInfoCollapsedWidget,
    expanded: SubscriptionInfoExpandedWidget,
    hidden: null
} as const

export const MainPageComponent = ({ isMobile, platform }: IMainPageComponentProps) => {
    const config = useAppConfig()
    const currentLang = useCurrentLang()
    const { setLanguage } = useAppConfigStoreActions()

    const pageCopy =
        currentLang === 'ru'
            ? {
                  brandSubtitle: 'Защищённое подключение',
                  privacyTitle: 'Ваша персональная ссылка',
                  privacyText:
                      'Откройте её на устройстве, которое хотите подключить. Не передавайте ссылку посторонним.',
                  footer: 'HAMVPN помогает оставаться на связи без сложных настроек'
              }
            : {
                  brandSubtitle: 'Secure connection',
                  privacyTitle: 'Your personal link',
                  privacyText:
                      'Open it on the device you want to connect. Do not share this link with anyone.',
                  footer: 'HAMVPN keeps you connected without complicated setup'
              }

    const brandName = config.brandingSettings.title

    const hasPlatformApps: Record<TSubscriptionPagePlatformKey, boolean> = {
        ios: Boolean(config.platforms.ios?.apps.length),
        android: Boolean(config.platforms.android?.apps.length),
        linux: Boolean(config.platforms.linux?.apps.length),
        macos: Boolean(config.platforms.macos?.apps.length),
        windows: Boolean(config.platforms.windows?.apps.length),
        androidTV: Boolean(config.platforms.androidTV?.apps.length),
        appleTV: Boolean(config.platforms.appleTV?.apps.length)
    }

    const atLeastOnePlatformApp = Object.values(hasPlatformApps).some((value) => value)

    const SubscriptionInfoBlockRenderer =
        SUBSCRIPTION_INFO_BLOCK_RENDERERS[config.uiConfig.subscriptionInfoBlockType]

    return (
        <Page>
            <Box className="header-wrapper" component="header" py="md">
                <Container maw={920} px={{ base: 'md', sm: 'lg', md: 'xl' }}>
                    <Group justify="space-between">
                        <Group gap="sm" style={{ userSelect: 'none' }} wrap="nowrap">
                            <Box className={classes.logoShell}>
                                <Image alt="HAMVPN" fit="contain" src="/assets/hamvpn-mascot.png" />
                            </Box>
                            <Stack gap={0}>
                                <Title c="white" fw={700} order={4} size="lg">
                                    {brandName}
                                </Title>
                                <Text className={classes.brandSubtitle} size="xs">
                                    {pageCopy.brandSubtitle}
                                </Text>
                            </Stack>
                        </Group>

                        <SubscriptionLinkWidget
                            hideGetLink={config.baseSettings.hideGetLinkButton}
                            supportUrl={config.brandingSettings.supportUrl}
                        />
                    </Group>
                </Container>
            </Box>

            <Container
                maw={920}
                className={classes.mainContainer}
                px={{ base: 'md', sm: 'lg', md: 'xl' }}
                py="xl"
                style={{ position: 'relative', zIndex: 1 }}
            >
                <Stack gap={isMobile ? 'lg' : 'xl'}>
                    {SubscriptionInfoBlockRenderer && (
                        <SubscriptionInfoBlockRenderer isMobile={isMobile} />
                    )}

                    <Box className={classes.privacyNote}>
                        <Box className={classes.privacyMarker} />
                        <Stack gap={3}>
                            <Text className={classes.privacyTitle} fw={650} size="sm">
                                {pageCopy.privacyTitle}
                            </Text>
                            <Text className={classes.privacyText} size="sm">
                                {pageCopy.privacyText}
                            </Text>
                        </Stack>
                    </Box>

                    {atLeastOnePlatformApp && (
                        <InstallationGuideConnector
                            BlockRenderer={
                                BLOCK_RENDERERS[config.uiConfig.installationGuidesBlockType]
                            }
                            hasPlatformApps={hasPlatformApps}
                            isMobile={isMobile}
                            platform={platform}
                        />
                    )}

                    <RawKeysWidget isMobile={isMobile} />

                    <Center className={classes.footer}>
                        <Stack align="center" gap="sm">
                            <Text c="dimmed" size="xs" ta="center">
                                {pageCopy.footer}
                            </Text>
                            <LanguagePicker
                                currentLang={currentLang}
                                locales={config.locales}
                                onLanguageChange={setLanguage}
                            />
                        </Stack>
                    </Center>
                </Stack>
            </Container>
        </Page>
    )
}
