import type { CancelablePromise } from "./core/CancelablePromise"
import { OpenAPI } from "./core/OpenAPI"
import { request as __request } from "./core/request"

export type EnvVariable = {
  key: string
  value: string
  description?: string | null
  created_at: string
  updated_at: string
}

export type EnvVariableListResponse = {
  total: number
  items: EnvVariable[]
}

export type EnvVariableUpdate = {
  value?: string
  description?: string | null
}

export class EnvService {
  /**
   * 모든 환경변수 조회
   */
  public static listEnvVariables(): CancelablePromise<EnvVariableListResponse> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/env",
    })
  }

  /**
   * 환경변수 수정
   */
  public static updateEnvVariable(data: {
    key: string
    requestBody: EnvVariableUpdate
  }): CancelablePromise<EnvVariable> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/env/{key}",
      path: {
        key: data.key,
      },
      body: data.requestBody,
      mediaType: "application/json",
      errors: {
        404: "Environment variable not found",
      },
    })
  }
}
