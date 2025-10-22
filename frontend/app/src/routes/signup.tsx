import { Container, Flex, Heading, Input, Text } from "@chakra-ui/react"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiAtSign, FiLock, FiUser } from "react-icons/fi"

import type { UserRegister } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { confirmPasswordRules, emailPattern, passwordRules } from "@/utils"

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

interface UserRegisterForm extends UserRegister {
  confirm_password: string
}

function SignUp() {
  const { signUpMutation } = useAuth()
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserRegisterForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      nickname: "",
      email: "",
      password: "",
      confirm_password: "",
    },
  })

  const onSubmit: SubmitHandler<UserRegisterForm> = (data) => {
    signUpMutation.mutate(data)
  }

  return (
    <Flex flexDir={{ base: "column", md: "row" }} justify="center" h="100vh">
      <Container
        as="form"
        onSubmit={handleSubmit(onSubmit)}
        h="100vh"
        maxW="sm"
        alignItems="stretch"
        justifyContent="center"
        gap={4}
        centerContent
      >
        <Heading size="lg" textAlign="center" mb={4}>
          회원가입
        </Heading>
        <Field invalid={!!errors.username} errorText={errors.username?.message}>
          <InputGroup w="100%" startElement={<FiUser />}>
            <Input
              {...register("username", {
                required: "사용자명을 입력해주세요",
                minLength: { value: 3, message: "최소 3자 이상 입력해주세요" },
              })}
              placeholder="사용자명"
              type="text"
            />
          </InputGroup>
        </Field>

        <Field invalid={!!errors.nickname} errorText={errors.nickname?.message}>
          <InputGroup w="100%" startElement={<FiAtSign />}>
            <Input
              {...register("nickname", { required: "닉네임을 입력해주세요" })}
              placeholder="닉네임"
              type="text"
            />
          </InputGroup>
        </Field>

        <Field invalid={!!errors.email} errorText={errors.email?.message}>
          <InputGroup w="100%" startElement={<FiAtSign />}>
            <Input
              {...register("email", {
                required: "이메일을 입력해주세요",
                pattern: emailPattern,
              })}
              placeholder="이메일"
              type="email"
            />
          </InputGroup>
        </Field>
        <PasswordInput
          type="password"
          startElement={<FiLock />}
          {...register("password", passwordRules())}
          placeholder="비밀번호"
          errors={errors}
        />
        <PasswordInput
          type="confirm_password"
          startElement={<FiLock />}
          {...register("confirm_password", confirmPasswordRules(getValues))}
          placeholder="비밀번호 확인"
          errors={errors}
        />
        <Button variant="solid" type="submit" loading={isSubmitting}>
          회원가입
        </Button>
        <Text>
          이미 계정이 있으신가요?{" "}
          <RouterLink to="/login" className="main-link">
            로그인
          </RouterLink>
        </Text>
      </Container>
    </Flex>
  )
}

export default SignUp
