import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface Photo {
  id: string;
  file_url: string;
  description: string;
  emotion: string;
  is_smiling: boolean;
  activity: string;
  location_type: string;
  location_detail: string;
  people_count: number;
  has_other_people: boolean;
  clothing_description: string;
  hair_length: string;
  is_funny: boolean;
  funniness_score: number;
  cuteness_score: number;
  objects: string[];
  season_guess: string;
  uploaded_at: string;
  relevance?: number;
}

export interface FilterOptions {
  emotions: string[];
  locations: string[];
  top_objects: string[];
}

export interface SearchRequest {
  query?: string;
  filters?: {
    emotions?: string[];
    location_types?: string[];
    objects?: string[];
    hair_length?: string;
  }
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:8000' }),
  tagTypes: ['Photo', 'Filters'],
  endpoints: (builder) => ({
    getPhotos: builder.query<Photo[], void>({
      query: () => '/api/photos',
      providesTags: ['Photo'],
    }),
    getFilterOptions: builder.query<FilterOptions, void>({
      query: () => '/api/filters/options',
      providesTags: ['Filters'],
    }),
    searchPhotos: builder.mutation<Photo[], SearchRequest>({
      query: (body) => ({
        url: '/api/search',
        method: 'POST',
        body,
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
      invalidatesTags: ['Photo', 'Filters'],
    }),
    deletePhoto: builder.mutation<void, string>({
      query: (photoId) => ({
        url: `/api/photos/${photoId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Photo', 'Filters'],
    }),
  }),
})

export const { 
  useGetPhotosQuery, 
  useGetFilterOptionsQuery,
  useSearchPhotosMutation, 
  useUploadPhotoMutation,
  useDeletePhotoMutation
} = api
