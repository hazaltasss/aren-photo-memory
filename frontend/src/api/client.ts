import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface Photo {
  id: string;
  file_url: string;
  description: string;
  emotion: string;
  is_smiling: boolean;
  uploaded_at: string;
  relevance?: number;
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:8000' }),
  tagTypes: ['Photo'],
  endpoints: (builder) => ({
    getPhotos: builder.query<Photo[], void>({
      query: () => '/api/photos',
      providesTags: ['Photo'],
    }),
    searchPhotos: builder.mutation<Photo[], string>({
      query: (query) => ({
        url: '/api/search',
        method: 'POST',
        body: { query, limit: 20 },
      }),
    }),
    uploadPhoto: builder.mutation<Photo, File>({
      query: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return {
          url: '/api/photos',
          method: 'POST',
          body: formData,
        }
      },
      invalidatesTags: ['Photo'],
    }),
  }),
})

export const { useGetPhotosQuery, useSearchPhotosMutation, useUploadPhotoMutation } = api
