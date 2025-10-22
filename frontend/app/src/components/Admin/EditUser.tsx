import {
  Button,
  DialogActionTrigger,
  DialogRoot,
  DialogTrigger,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Controller, type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type UserPublic, UsersService, type UserUpdate } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditUserProps {
  user: UserPublic
}

interface UserUpdateForm extends UserUpdate {
  confirm_password?: string
}

const EditUser = ({ user }: EditUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    control,
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: user,
  })

  const mutation = useMutation({
    mutationFn: (data: UserUpdateForm) =>
      UsersService.updateUser({ userId: user.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("사용자 정보가 성공적으로 업데이트되었습니다.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const onSubmit: SubmitHandler<UserUpdateForm> = async (data) => {
    if (data.password === "") {
      data.password = undefined
    }
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          <FaExchangeAlt fontSize="16px" />
          사용자 수정
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>사용자 수정</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>아래 정보를 수정한 뒤 저장하세요.</Text>
            <VStack gap={4}>
              <Field
                invalid={!!errors.username}
                errorText={errors.username?.message}
                label="사용자명"
              >
                <Input
                  {...register("username", {
                    minLength: {
                      value: 3,
                      message: "최소 3자 이상 입력해주세요",
                    },
                  })}
                  placeholder="사용자명"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.nickname}
                errorText={errors.nickname?.message}
                label="닉네임"
              >
                <Input
                  {...register("nickname")}
                  placeholder="닉네임"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.email}
                errorText={errors.email?.message}
                label="이메일"
              >
                <Input
                  {...register("email", {
                    required: "이메일을 입력해주세요",
                    pattern: emailPattern,
                  })}
                  placeholder="이메일"
                  type="email"
                />
              </Field>

              <Field
                invalid={!!errors.password}
                errorText={errors.password?.message}
                label="비밀번호 설정"
              >
                <Input
                  {...register("password", {
                    minLength: {
                      value: 8,
                      message: "비밀번호는 8자 이상이어야 합니다",
                    },
                  })}
                  placeholder="비밀번호"
                  type="password"
                />
              </Field>

              <Field
                invalid={!!errors.confirm_password}
                errorText={errors.confirm_password?.message}
                label="비밀번호 확인"
              >
                <Input
                  {...register("confirm_password", {
                    validate: (value) =>
                      value === getValues().password ||
                      "비밀번호가 일치하지 않습니다",
                  })}
                  placeholder="비밀번호 확인"
                  type="password"
                />
              </Field>
            </VStack>

            <Flex mt={4} direction="column" gap={4}>
              <Controller
                control={control}
                name="is_superuser"
                render={({ field }) => (
                  <Field disabled={field.disabled} colorPalette="teal">
                    <Checkbox
                      checked={field.value ?? false}
                      onCheckedChange={({ checked }) => field.onChange(checked)}
                    >
                      관리자 권한 부여
                    </Checkbox>
                  </Field>
                )}
              />
              <Controller
                control={control}
                name="is_active"
                render={({ field }) => (
                  <Field disabled={field.disabled} colorPalette="teal">
                    <Checkbox
                      checked={field.value ?? false}
                      onCheckedChange={({ checked }) => field.onChange(checked)}
                    >
                      활성 사용자
                    </Checkbox>
                  </Field>
                )}
              />
            </Flex>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                취소
              </Button>
            </DialogActionTrigger>
            <Button variant="solid" type="submit" loading={isSubmitting}>
              저장
            </Button>
          </DialogFooter>
          <DialogCloseTrigger />
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default EditUser
