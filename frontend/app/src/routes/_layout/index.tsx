import { useEffect } from "react"

import { createFileRoute, useNavigate } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const navigate = useNavigate({ from: Route.fullPath })

  useEffect(() => {
    const destination = currentUser?.is_superuser ? "/admin" : "/settings"
    navigate({ to: destination, replace: true })
  }, [currentUser?.is_superuser, navigate])

  return null
}
