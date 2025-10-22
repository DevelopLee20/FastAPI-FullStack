import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"

import EnvironmentVariables from "@/components/UserSettings/EnvironmentVariables"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/admin/env")({
  component: AdminEnvironmentVariables,
})

function AdminEnvironmentVariables() {
  const { user: currentUser } = useAuth()
  const navigate = useNavigate({ from: Route.fullPath })

  useEffect(() => {
    if (currentUser && !currentUser.is_superuser) {
      navigate({ to: "/settings", replace: true })
    }
  }, [currentUser, navigate])

  if (!currentUser?.is_superuser) {
    return null
  }

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12} pb={6}>
        환경 변수 관리
      </Heading>
      <EnvironmentVariables />
    </Container>
  )
}
