import { User } from './user.model';

export interface Comment {
  id: number;
  task: number;
  author: User;
  text: string;
  created_at: string;
}