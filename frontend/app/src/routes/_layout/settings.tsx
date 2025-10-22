import { Container, Heading, Tabs } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import Appearance from "@/components/UserSettings/Appearance"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import UserInformation from "@/components/UserSettings/UserInformation"
import useAuth from "@/hooks/useAuth"

const baseTabs = [
  { value: "my-profile", title: "내 프로필", component: UserInformation },
  { value: "password", title: "비밀번호", component: ChangePassword },
  { value: "appearance", title: "테마", component: Appearance },
]

const dangerTab = {
  value: "danger-zone",
  title: "위험 영역",
  component: DeleteAccount,
}

const settingsSearchSchema = z.object({ tab: z.string().optional() })

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  validateSearch: (search) => settingsSearchSchema.parse(search),
})

function UserSettings() {
  const { user: currentUser } = useAuth()
  const finalTabs = currentUser?.is_superuser
    ? baseTabs
    : [...baseTabs, dangerTab]
  const { tab } = Route.useSearch()
  const defaultTab =
    tab && finalTabs.find((t) => t.value === tab) ? tab : "my-profile"

  if (!currentUser) {
    return null
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        사용자 설정
      </Heading>

      <Tabs.Root defaultValue={defaultTab} variant="subtle">
        <Tabs.List>
          {finalTabs.map((tab) => (
            <Tabs.Trigger key={tab.value} value={tab.value}>
              {tab.title}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        {finalTabs.map((tab) => (
          <Tabs.Content key={tab.value} value={tab.value}>
            <tab.component />
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </Container>
  )
}
