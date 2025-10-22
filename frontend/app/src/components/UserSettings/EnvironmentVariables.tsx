import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Spinner,
  Table,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"

import {
  type ApiError,
  EnvService,
  type EnvVariable,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const EnvironmentVariables = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const [editingKey, setEditingKey] = useState<string | null>(null)
  const [draftValue, setDraftValue] = useState("")
  const [draftDescription, setDraftDescription] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["envVariables"],
    queryFn: async () => {
      const response = await EnvService.listEnvVariables()
      return response.items
    },
  })

  const mutation = useMutation({
    mutationFn: (payload: { key: string; value?: string; description?: string }) =>
      EnvService.updateEnvVariable({
        key: payload.key,
        requestBody: {
          value: payload.value,
          description: payload.description ?? null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Environment variable updated.")
      setEditingKey(null)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["envVariables"] })
    },
  })

  const envVariables = useMemo<EnvVariable[]>(() => data ?? [], [data])

  const startEdit = (envVar: EnvVariable) => {
    setEditingKey(envVar.key)
    setDraftValue(envVar.value ?? "")
    setDraftDescription(envVar.description ?? "")
  }

  const cancelEdit = () => {
    setEditingKey(null)
  }

  const saveEdit = () => {
    if (!editingKey) return
    mutation.mutate({
      key: editingKey,
      value: draftValue,
      description: draftDescription.trim() === "" ? undefined : draftDescription,
    })
  }

  if (isLoading) {
    return (
      <Flex minH="40" align="center" justify="center">
        <Spinner />
      </Flex>
    )
  }

  return (
    <Container maxW="full">
      <VStack align="stretch" spacing={6}>
        <Box>
          <Heading size="sm" py={4}>
            Environment Variables
          </Heading>
          <Text color="fg.muted">
            View and update runtime environment variables stored in PostgreSQL
            and cached in Redis.
          </Text>
        </Box>

        {envVariables.length === 0 ? (
          <Text color="fg.muted">No environment variables found.</Text>
        ) : (
          <Table.Root variant="simple">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader width="20%">Key</Table.ColumnHeader>
                <Table.ColumnHeader width="35%">Value</Table.ColumnHeader>
                <Table.ColumnHeader>Description</Table.ColumnHeader>
                <Table.ColumnHeader width="15%" textAlign="right">
                  Actions
                </Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {envVariables.map((envVar) => {
                const isEditing = editingKey === envVar.key
                return (
                  <Table.Row key={envVar.key}>
                    <Table.Cell fontWeight="medium">{envVar.key}</Table.Cell>
                    <Table.Cell>
                      {isEditing ? (
                        <Textarea
                          value={draftValue}
                          onChange={(event) => setDraftValue(event.target.value)}
                          size="sm"
                        />
                      ) : (
                        <Text whiteSpace="pre-wrap">{envVar.value}</Text>
                      )}
                    </Table.Cell>
                    <Table.Cell>
                      {isEditing ? (
                        <Textarea
                          value={draftDescription}
                          onChange={(event) =>
                            setDraftDescription(event.target.value)
                          }
                          size="sm"
                        />
                      ) : (
                        <Text color={envVar.description ? "inherit" : "fg.muted"}>
                          {envVar.description || "—"}
                        </Text>
                      )}
                    </Table.Cell>
                    <Table.Cell>
                      <Flex justify="flex-end" gap={2}>
                        {isEditing ? (
                          <>
                            <Button
                              size="sm"
                              variant="solid"
                              onClick={saveEdit}
                              loading={mutation.isPending}
                            >
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="subtle"
                              colorPalette="gray"
                              onClick={cancelEdit}
                              disabled={mutation.isPending}
                            >
                              Cancel
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            variant="subtle"
                            onClick={() => startEdit(envVar)}
                          >
                            Edit
                          </Button>
                        )}
                      </Flex>
                    </Table.Cell>
                  </Table.Row>
                )
              })}
            </Table.Body>
          </Table.Root>
        )}
      </VStack>
    </Container>
  )
}

export default EnvironmentVariables
