import { OpenAPI, UsersService } from "../../src/client"

OpenAPI.BASE = `${process.env.VITE_API_URL}`

export const createUser = async ({
  email,
  password,
  fullName = "Test User",
}: {
  email: string
  password: string
  fullName?: string
}) => {
  return await UsersService.registerUser({
    requestBody: {
      email,
      password,
      full_name: fullName,
    },
  })
}
