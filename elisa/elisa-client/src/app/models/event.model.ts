export class Event {
  id: string;
  idType: number;
  idCourse: number;
  idTeacher: number;
  idRoom: number;
  day: number;
  startTime: number;
  endTime: number;


  constructor(id: string, idType: number, idCourse: number, idTeacher: number, idRoom: number, day: number, startTime: number, endTime: number) {
    this.id = id;
    this.idType = idType;
    this.idCourse = idCourse;
    this.idTeacher = idTeacher;
    this.idRoom = idRoom;
    this.day = day;
    this.startTime = startTime;
    this.endTime = endTime;
  }
}
