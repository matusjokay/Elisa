import { TimetableComment } from './comment';
import { RequirementEvent } from './requirement-event';
import * as moment from 'moment';
import { Room } from './room';
import { EventInput } from '@fullcalendar/core/structs/event';

export class Requirement {

  private static DaysMap = {
    1: 'monday',
    2: 'tuesday',
    3: 'wednesday',
    4: 'thursday',
    5: 'friday',
  };

  private static EventTypesMap = {
    1 : 'green',
    2 : 'yellow',
    3 : 'red',
  };

  private static StatusMap = {
    created : 1,
    edited : 2,
    rejected : 3,
    approved : 4
  };

  public static StatusValues = {
    1 : 'Created',
    2 : 'Edited',
    3 : 'Rejected',
    4 : 'Approved'
  };

  private static TypesMap = {
    1 : 'Lecture',
    2 : 'Seminar'
  };

  public id?: number;
  public created_by: number | { id: number, fullname: string };
  public teacher: number | { id: number, fullname: string };
  public status: number;
  public requirement_type: number;
  public teacher_type?: number;
  public last_updated?: string;
  public for_department?: number;
  public events: RequirementEvent[];
  public comments?: TimetableComment[];

  public static toBasicDateFormat(dateString: string) {
    return moment.utc(dateString).format('LL');
  }

  public static generateEventCalendar(events: RequirementEvent[], rooms?: Room[]): EventInput[] {
    let index = 1;
    const calendarEvents = events.map(obj => {
      return {
        // startTime: obj.start.toLocaleTimeString('sk-SK'),
        // endTime: obj.end.toLocaleTimeString('sk-SK'),
        startTime: obj.start,
        endTime: obj.end,
        // resourceId: this.DaysMap[obj.day],
        resourceId: obj.day,
        backgroundColor: this.EventTypesMap[obj.event_type],
        // groupId: obj.course,
        id: index++,
        course: obj.course,
        title: rooms.find(r => r.id === obj.room).name,
        type: obj.event_type
      };
    });
    return calendarEvents;
  }

  public static toStatusValue(key: string) {
    return this.StatusMap[key];
  }
}
