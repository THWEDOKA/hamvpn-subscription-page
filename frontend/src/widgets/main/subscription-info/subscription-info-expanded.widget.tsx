import { Box, Card, Group, SimpleGrid, Stack, Text, ThemeIcon, Title } from '@mantine/core'
import {
    IconAlertCircle,
    IconArrowsUpDown,
    IconCalendar,
    IconCheck,
    IconUserScan,
    IconX
} from '@tabler/icons-react'

import { useTranslation } from '@shared/hooks'
import { formatDate, getExpirationTextUtil } from '@shared/utils/config-parser'

import { useSubscription } from '@entities/subscription-info-store'

import classes from './subscription-info-expanded.module.css'

interface IProps {
    isMobile: boolean
}

interface IMetricProps {
    icon: React.ReactNode
    label: string
    value: string
}

const Metric = ({ icon, label, value }: IMetricProps) => (
    <Box className={classes.metric}>
        <Group align="flex-start" gap="sm" wrap="nowrap">
            <Box className={classes.metricIcon}>{icon}</Box>
            <Stack gap={3} style={{ minWidth: 0 }}>
                <Text className={classes.metricLabel} size="xs">
                    {label}
                </Text>
                <Text className={classes.metricValue} fw={650} size="sm">
                    {value}
                </Text>
            </Stack>
        </Group>
    </Box>
)

export const SubscriptionInfoExpandedWidget = ({ isMobile }: IProps) => {
    const { t, currentLang, baseTranslations } = useTranslation()
    const subscription = useSubscription()
    const { user } = subscription

    const isActive = user.userStatus === 'ACTIVE' && user.daysLeft >= 0
    const isExpiringSoon = isActive && user.daysLeft <= 3

    const copy =
        currentLang === 'ru'
            ? {
                  eyebrow: 'ВАША ПОДПИСКА',
                  active: 'Подписка активна',
                  expiring: 'Подписка скоро закончится',
                  inactive: 'Подписка не активна',
                  account: 'Аккаунт',
                  validUntil: 'Действует до',
                  traffic: 'Использовано трафика'
              }
            : {
                  eyebrow: 'YOUR SUBSCRIPTION',
                  active: 'Subscription is active',
                  expiring: 'Subscription expires soon',
                  inactive: 'Subscription is inactive',
                  account: 'Account',
                  validUntil: 'Valid until',
                  traffic: 'Traffic usage'
              }

    const state = isExpiringSoon ? 'warning' : isActive ? 'active' : 'inactive'
    const title = isExpiringSoon ? copy.expiring : isActive ? copy.active : copy.inactive
    const statusText = isActive ? t(baseTranslations.active) : t(baseTranslations.inactive)
    const StateIcon = isExpiringSoon ? IconAlertCircle : isActive ? IconCheck : IconX
    const bandwidthValue = `${user.trafficUsed} / ${user.trafficLimit === '0' ? '∞' : user.trafficLimit}`

    return (
        <Card className={`${classes.root} ${classes[state]}`} p={0} radius="xl">
            <Box className={classes.glow} />
            <Stack className={classes.content} gap={isMobile ? 'lg' : 'xl'}>
                <Group align="flex-start" justify="space-between" wrap="nowrap">
                    <Group align="flex-start" gap={isMobile ? 'sm' : 'md'} wrap="nowrap">
                        <ThemeIcon
                            className={classes.stateIcon}
                            radius="xl"
                            size={isMobile ? 44 : 52}
                            variant="light"
                        >
                            <StateIcon size={isMobile ? 22 : 26} stroke={1.9} />
                        </ThemeIcon>

                        <Stack gap={5} style={{ minWidth: 0 }}>
                            <Text className={classes.eyebrow} fw={700} size="xs">
                                {copy.eyebrow}
                            </Text>
                            <Title className={classes.title} order={2}>
                                {title}
                            </Title>
                            <Text className={classes.expiration} size="sm">
                                {getExpirationTextUtil(
                                    user.expiresAt,
                                    currentLang,
                                    baseTranslations
                                )}
                            </Text>
                        </Stack>
                    </Group>

                    <Box className={classes.statusPill} data-state={state}>
                        <Box className={classes.statusDot} />
                        <Text fw={650} size="xs">
                            {statusText}
                        </Text>
                    </Box>
                </Group>

                <SimpleGrid cols={{ base: 1, xs: 3 }} spacing="xs" verticalSpacing="xs">
                    <Metric
                        icon={<IconUserScan size={18} stroke={1.8} />}
                        label={copy.account}
                        value={user.username}
                    />
                    <Metric
                        icon={<IconCalendar size={18} stroke={1.8} />}
                        label={copy.validUntil}
                        value={formatDate(user.expiresAt, currentLang, baseTranslations)}
                    />
                    <Metric
                        icon={<IconArrowsUpDown size={18} stroke={1.8} />}
                        label={copy.traffic}
                        value={bandwidthValue}
                    />
                </SimpleGrid>
            </Stack>
        </Card>
    )
}
