export interface SemesterVersion {
  id: number;
  name: string;
  status: string;
  period?: number;
  last_updated?: Date;
}
