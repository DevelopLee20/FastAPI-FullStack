import { Table } from "@chakra-ui/react"
import { SkeletonText } from "../ui/skeleton"

const PendingUsers = () => (
  <Table.Root size={{ base: "sm", md: "md" }}>
    <Table.Header>
      <Table.Row>
        <Table.ColumnHeader w="sm">닉네임</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">이메일</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">역할</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">상태</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">작업</Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {[...Array(5)].map((_, index) => (
        <Table.Row key={index}>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table.Root>
)

export default PendingUsers
