import { User } from './user';

export interface TimetableComment {
  id?: number;
  type?: number;
  text: string;
  created_at?: Date;
  comment_by?: User;
  comment_by_id?: number;
}
