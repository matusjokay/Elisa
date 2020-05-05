import {Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators} from '@angular/forms';
import {EventInput} from '@fullcalendar/core/structs/event';
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';
import interactionPlugin from '@fullcalendar/interaction';
import {RequirementService} from '../../../services/requirement.service';
import {CourseService} from '../../../services/course.service';
import { RoomType, Room } from 'src/app/models/room';
import { User } from 'src/app/models/user';
import { CourseRole } from 'src/app/models/course-users.model';
import { UserService } from 'src/app/services/user.service';
import { RoomService } from 'src/app/services/room.service';
import { MatSelectChange } from '@angular/material/select';
import { Course } from 'src/app/models/course';
import { UserSearchComponent } from 'src/app/common/user-search/user-search.component';
import { FullCalendarComponent } from '@fullcalendar/angular';
import { BaseService } from 'src/app/services/base-service.service';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from 'src/app/common/confirm-dialog/confirm-dialog.component';
import { MatRadioChange } from '@angular/material/radio';
import { TimetableComment } from 'src/app/models/comment';
import { Router, ActivatedRoute } from '@angular/router';
import { Requirement } from 'src/app/models/requirement';
import { RoomEquipment } from 'src/app/models/room-equipment';
import { Department } from 'src/app/models/department';
import { DepartmentService } from 'src/app/services/department.service';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';
import * as _ from 'lodash';

@Component({
  selector: 'app-requirement-form',
  templateUrl: './requirement-form.component.html',
  styleUrls: ['./requirement-form.component.less']
})
export class RequirementFormComponent implements OnInit, AfterViewInit {

  requirementForm: FormGroup;
  optionsUsers: any;
  loading: boolean;
  loadingText: string;
  optionsCourses: Course[];
  studentNumberCourse: {id: number, total: number}[];
  user: User;
  course: Course;
  userSelected: boolean;
  courseRoles: CourseRole[];
  roomTypes: RoomType[];
  rooms: Room[];
  roomEquipment: RoomEquipment[] = [];
  choosenRooms: Room[] = [];
  choosenCourses: Course[] = [];
  editChoosenRooms: Room[];
  editChoosenCourses: Course[];
  selectedRoom: Room;
  editRequirement: Requirement;
  backupRequirement: Requirement;
  edit: boolean;
  forDepartment: Department;
  requirementNotes: TimetableComment[];
  editRequirementNotes: TimetableComment[];
  @ViewChild('searcher') searcher: UserSearchComponent;
  disable = true;
  requirementType = 1;
  eventId = 1;
  removeEvents = false;

  users: User[];

  types = [
    { id: 1, name: 'suitable', color: 'green' },
    { id: 2, name: 'unsuitable', color: 'yellow' },
    { id: 3, name: 'unavailable', color: 'red' },
  ];
  activeType = { id: 1, name: 'suitable', color: 'green' };

  @ViewChild('calendar') calendar: FullCalendarComponent;
  tooltipText: string;
  tooltipShow: boolean;
  calendarHeader;
  calendarPlugins;
  calendarEvents: EventInput[];
  editCalendarEvents: EventInput[];
  resources;
  duration;

  constructor(
    private requirementService: RequirementService,
    private coursesService: CourseService,
    private departmentService: DepartmentService,
    private userService: UserService,
    private roomService: RoomService,
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private snackbar: SnackbarComponent,
    private dialog: MatDialog,
    private baseService: BaseService
  ) {}

  ngOnInit() {
    this.initOptions();
    this.route.queryParams.subscribe(
      (params) => {
        if (params['requirementId']) {
          this.edit = true;
          this.fetchDepartment(params['departmentId']);
          this.fetchEditableRequirement(params['requirementId']);
        } else {
          this.edit = false;
          this.fetchDepartment(params['departmentId']);
          this.requirementForm = this.createFormGroup();
        }
      }
    );
    this.requirementForm = this.fb.group({
      room_type_id: [],
      room_id: [{ value: '', disabled: true }],
      user_role_id: [],
      teacher_id: [],
      course_id: [{ value: '', disabled: true }],
      comment: [],
    });
  }

  ngAfterViewInit(): void {
    this.resetSearcher();
  }

  createFormGroup() {
    return !this.edit ? this.fb.group({
      room_type_id: [{ value: '', disabled: true }],
      room_id: [{ value: '', disabled: true }, Validators.required],
      user_role_id: [],
      teacher_id: [{ value: '' }, Validators.required],
      course_id: [{ value: '', disabled: true }, Validators.required],
      comment: [],
    }) : this.fb.group({
      room_type_id: [{ value: '' }],
      room_id: [{ value: '', disabled: true }, Validators.required],
      teacher_id: [{ value: this.editRequirement.teacher['id'], disabled: true }, Validators.required],
      course_id: [{ value: '' }, Validators.required],
      comment: [],
    });
  }

  fetchDepartment(depId: number) {
    this.onRequestSent('Fetching department data...');
    this.departmentService.getDepartment(depId).subscribe(
      (success) => {
        this.forDepartment = success;
        if (!this.edit) {
          this.loadData();
        }
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          `Failed to assign department for requirement!`,
          'Close',
          this.snackbar.styles.failure);
        setTimeout(() => {
          this.onRequestDone();
          this.router.navigate(['requirement-list']);
        }, 1000);
      }
    );
  }

  loadData() {
    this.onRequestSent('Fetching course roles...');
    this.userService.getUserCourseRoles().subscribe(
      (success) => {
        this.courseRoles = success;
        this.fetchRoomTypes();
        // this.initUsers();
        // this.fetchUsersByDepartment();
      },
      (error) => console.error(error)
    );
  }

  fetchEditableRequirement(reqId: number) {
    this.onRequestSent('Fetching created requirement...');
    this.requirementService.getRequirement(reqId).subscribe(
      (success) => {
        this.editRequirement = success;
        this.backupRequirement = _.cloneDeep(this.editRequirement);
        this.requirementNotes = success.comments;
        this.editRequirementNotes = success.comments;
        this.requirementForm = this.createFormGroup();
        this.fetchRoomTypes();
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          `Failed to fetch requirement to edit!`,
          'Close',
          this.snackbar.styles.failure);
      }
    ).add(() => this.onRequestDone());
  }

  initUsers() {
    this.onRequestSent('Initializing users...');
    this.userService.getCachedAllUsers().subscribe(
      (success) => this.users = success,
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  fetchUsersByDepartment() {
    this.onRequestSent('Initializing users by department...');
    this.userService.getUsersByDepartment(this.forDepartment).subscribe(
      (success) => this.users = success,
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  onRequirementTypeChange(event: MatRadioChange) {
    this.requirementForm.reset();
    this.resetSearcher();
    this.calendarEvents = [];
  }

  onUserRoleType(event: MatSelectChange) {
    if (!event.value) {
      this.searcher.searchForm.get('name').disable();
      return;
    }
    this.onRequestSent('Adjusting users...');
    this.userService.getTeachersOrStudents(event.value).subscribe(
      (success) => {
        this.users = this.users.filter(user => success.some(userByRole => user.id === userByRole.userId));
        this.searcher.searchForm.get('name').enable();
        this.searcher.searchForm.get('name').setValue('');
      },
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  onCourseChange(event: MatSelectChange){
    this.course = event.value ? this.optionsCourses.find(c => c.id === event.value) : null;
  }

  onRoomTypeChange(event: MatSelectChange) {
    console.log(event.value);
    if (event.value) {
      this.onRequestSent('Fetching rooms...')
      this.roomService.getRoomsByType(event.value).subscribe(
        (success) => {
          this.rooms = success;
          this.requirementForm.get('room_id').enable();
          const roomIds = success.map(r => r.id);
          this.fetchRoomsEquipment(roomIds);
        },
        (error) => console.error(error)
      );
    } else {
      this.requirementForm.get('room_id').disable();
    }
  }

  fetchRoomsEquipment(rooms: number[]) {
    this.onRequestSent('Fetching equipment of rooms...');
    this.roomService.getRoomEquipmentByIds(rooms).subscribe(
      (success) => this.roomEquipment = success,
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  getEquipmentText(room: Room) {
    let result = '';
    this.roomEquipment.forEach(re => {
      if (re.room_id === room.id) {
        result += `Equipment: ${re.equipment.name} | Count: ${re.count}\n`;
      }
    });
    return result;
  }

  onRoomChange(event: MatSelectChange) {
    console.log(event.value);
    if (event.value) {
      this.selectedRoom = this.rooms.find(r => r.id === event.value);
      this.requirementForm.get('course_id').enable();
    } else {
      this.requirementForm.get('course_id').disable();
      this.selectedRoom = null;
    }
  }

  fetchRoomTypes() {
    this.onRequestSent('Fetching room types...');
    this.roomService.getRoomTypes().subscribe(
      (success) => {
        this.roomTypes = success;
        if (!this.edit) {
          // this.initUsers();
          this.fetchUsersByDepartment();
        } else {
          this.fetchCoursesByUserAndRole('Adjusting courses for teachers role...', this.backupRequirement.teacher_type);
        }
      },
      (error) => console.error(error)
    );
  }

  onSelectedUser(event: User) {
    if (!this.user) {
      this.user = event;
    } else {
      this.user = event;
      this.reset();
    }
    this.requirementForm.get('teacher_id').setValue(event.id);
    const roleId = this.requirementForm.get('user_role_id').value;
    this.fetchCoursesByUserAndRole('Adjusting courses by User role...', roleId);
  }

  getNumberOfStudentsOnCourse(courseId: number): string {
    const record = this.studentNumberCourse.find(r => r.id === courseId);
    return record ? `Students: ${record.total}` : '';
  }

  fetchCoursesByUserAndRole(msg: string, roleId: number) {
    this.onRequestSent(msg);
    const userId = !this.edit ? this.user.id : this.editRequirement.teacher['id'];
    this.coursesService.getCoursesByUserAndRole(userId, roleId).subscribe(
      (success) => {
        this.optionsCourses = success;
        this.choosenCourses = this.edit ? success : [];
        if (this.edit) {
          this.editChoosenCourses = _.cloneDeep(this.choosenCourses);
          this.fetchRoomsByEventIds();
        }
        this.fetchStudentNumbersOnCourses();
      },
      (error) => console.error(error)
    // ).add(() => this.onRequestDone());
    );
  }

  fetchStudentNumbersOnCourses() {
    this.onRequestSent('Fetching number of students on courses...');
    const courseIds = this.optionsCourses.map(course => course.id);
    this.coursesService.getNumberOfStudentsOnCourses(courseIds).subscribe(
      (success) => this.studentNumberCourse = success,
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  fetchRoomsByEventIds() {
    const roomIds = this.backupRequirement.events.reduce((filtered, event) => {
      if (!filtered.includes(event.room)) {
        filtered.push(event.room);
      } else {
        return filtered;
      }
      return filtered;
    }, []);
    this.onRequestSent('Fetching events rooms...');
    this.roomService.getRoomsByIds(roomIds).subscribe(
      (success) => {
        this.choosenRooms = this.edit ? success : [];
        if (this.edit) {
          this.editChoosenRooms = _.cloneDeep(this.choosenRooms);
        }
        const events = Requirement.generateEventCalendar(this.backupRequirement.events, success);
        this.eventId = Number(events[events.length - 1].id);
        this.eventId++;
        this.calendarEvents = [...events];
        this.editCalendarEvents = _.cloneDeep(this.calendarEvents);
      },
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  onSelected(event: boolean) {
    if (event) {
      this.requirementForm.get('room_type_id').enable();
    } else {
      this.requirementForm.get('room_type_id').disable();
    }
  }

  // Adhoc solution for tooltip popping instead of
  // material tooltip which didn't appear due to FC
  // css classes
  // TODO: using an external library with more
  // sophisticated features
  onMouseEnter(event, tooltip) {
    if (!event.event.extendedProps.course || this.removeEvents) {
      return;
    }
    const courseId = Number(event.event.extendedProps.course);
    const course = this.choosenCourses.find(c => c.id === courseId);
    if (!course) {
      return;
    }
    this.tooltipText = course.name;
    this.tooltipShow = true;
    const rect = event.el.getBoundingClientRect();
    const leftOffset = rect.left - 15;
    const topOffset = rect.top + 18;
    tooltip.style['top'] = `${topOffset}px`;
    tooltip.style['left'] = `${leftOffset}px`;
  }

  onMouseLeave() {
    setTimeout(() => this.tooltipShow = false);
  }

  onSubmit() {
    console.log('before submitting form');
    console.log(this.requirementForm);
    const events = this.calendarEvents.reduce((filtered, event) => {
      if (!event.course || !event.title) {
        return filtered;
      } else {
        const room = this.choosenRooms.find(r => r.name === event.title);
        filtered.push({
          start: event.startTime,
          end: event.endTime,
          event_type: event.type,
          day: Number(event.resourceId),
          course: Number(event.course),
          room: room ? room.id : null
        });
      }
      return filtered;
    }, []);

    if (!this.edit) {
      const comments: TimetableComment[] = (
        this.requirementForm.value.comment ? [
          { text: this.requirementForm.value.comment, type: 1,
            comment_by_id: this.baseService.getUserId()
          }
        ] : []);
      const requestPost  = {
        created_by: this.baseService.getUserId(),
        teacher: this.requirementForm.value.teacher_id,
        comments: comments,
        events: events,
        status: Requirement.toStatusValue('created'),
        requirement_type: this.requirementType,
        for_department: this.forDepartment.id,
        teacher_type: this.requirementForm.value.user_role_id
      };
      console.log('finished objecT');
      console.log(requestPost);
      this.onRequestSent('Creating requirement...');
      this.requirementService.createRequirement(requestPost).subscribe(
        (success) => {
          this.snackbar.openSnackBar(
            `Successfully created requirement!`,
            'Close',
            this.snackbar.styles.success);
            this.onRequestSent('Going back to Requirements...');
            setTimeout(() => {
              this.onRequestDone();
              this.router.navigate(['requirement-list']);
            }, 1000);
        }, (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to create requirement!`,
            'Close',
            this.snackbar.styles.failure);
        }
      );
    } else {
      const comments: TimetableComment[] = this.requirementNotes.map(note => {
        return {
          id: !note.id ? null : note.id,
          text: note.text,
          type: 1,
          comment_by_id: this.baseService.getUserId()
        };
      });
      const requestUpdate = {
        id: this.editRequirement.id,
        created_by: this.editRequirement.created_by['id'],
        teacher: this.editRequirement.teacher['id'],
        comments: comments,
        events: events,
        status: Requirement.toStatusValue('edited'),
        requirement_type: this.editRequirement.requirement_type,
        teacher_type: this.editRequirement.teacher_type,
        for_department: this.editRequirement.for_department
      };
      this.onRequestSent('Editing requirement...');
      this.requirementService.editRequirement(requestUpdate).subscribe(
        (success) => {
          this.snackbar.openSnackBar(
            `Successfully updated requirement!`,
            'Close',
            this.snackbar.styles.success);
            this.onRequestSent('Going back to Requirements...');
            setTimeout(() => {
              this.onRequestDone();
              this.router.navigate(['requirement-list']);
            }, 1000);
        }, (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to update requirement!`,
            'Close',
            this.snackbar.styles.failure);
        }
      );
    }
  }

  handleSelect(arg) {
    if (!this.selectedRoom || !this.course || this.removeEvents) {
      console.log('empty event!');
      return;
    }
    this.choosenRooms = this.selectedRoom ? [...this.choosenRooms, this.selectedRoom] : this.choosenRooms;
    this.choosenCourses = this.course ? [...this.choosenCourses, this.course] : this.choosenCourses;
    this.calendarEvents = [...this.calendarEvents, // add new event data. must create new array
      {
        startTime: arg.start.toLocaleTimeString('sk-SK'),
        endTime: arg.end.toLocaleTimeString('sk-SK'),
        resourceId: arg.resource.id,
        id: this.eventId++,
        title: !this.selectedRoom ? '' : this.selectedRoom.name,
        course: !this.course ? '' : this.course.id,
        backgroundColor: this.activeType.color,
        type: this.activeType.id
      }
    ];
  }

  onRequestSent(msg: string) {
    this.loadingText = msg;
    this.loading = true;
  }

  onRequestDone() {
    this.loadingText = '';
    this.loading = false;
  }

  onNoteAdd() {
    const text = this.requirementForm.controls.comment.value;
    if (!text) {
      return;
    }
    const noteObj = {
      text: text,
      type: 1,
      comment_by: { id: this.baseService.getUserId(), fullname: this.baseService.getUserName() }
    };
    this.requirementNotes = [...this.requirementNotes, noteObj];
    this.requirementForm.controls.comment.setValue('');
  }

  onEventClick(event) {
    console.log(event);
    if (this.removeEvents) {
      const eventId = Number(event.event.id);
      this.calendarEvents = this.calendarEvents.filter(e => e.id !== eventId);
    }
    console.log(this.calendarEvents);
  }

  onSlideDelete(event: MatSlideToggleChange) {
    this.removeEvents = event.checked;
  }

  selectType(id){
    this.activeType = this.types.find( type => {
      return type.id === id;
    });
  }

  noEvents() {
    return Array.isArray(this.calendarEvents) && this.calendarEvents.length ? false : true;
  }

  checkIfChanged() {
    return this.edit ? _.isEqual(this.editCalendarEvents, this.calendarEvents) &&
           _.isEqual(this.editRequirementNotes, this.requirementNotes) :
           _.isEmpty(this.calendarEvents);
  }

  reset() {
    if (!this.edit) {
      this.calendarEvents = [];
      this.requirementForm.controls.comment.setValue('');
    } else {
      this.calendarEvents = [...this.editCalendarEvents];
      this.requirementNotes = [...this.editRequirementNotes];
      this.choosenRooms = _.cloneDeep(this.editChoosenRooms);
      this.choosenCourses = _.cloneDeep(this.editChoosenCourses);
    }
  }

  resetSearcher() {
    if (!this.edit) {
      setTimeout(() => this.searcher.searchForm.get('name').disable());
    }
  }

  initOptions() {
    this.calendarHeader = false;
    this.calendarPlugins = [resourceTimelinePlugin, interactionPlugin];

    this.calendarEvents = [];

    this.resources = [
      {id: 1, title: 'Monday'},
      {id: 2, title: 'Tuesday'},
      {id: 3, title: 'Wednesday'},
      {id: 4, title: 'Thursday'},
      {id: 5, title: 'Friday'},
    ];
    this.duration = 5;
    this.activeType = this.types.find(function (type) {
      return type.id === 1;
    });
  }

  onEventRender(info) {
    info.el.style['height'] = '5vh';
    info.el.style['color'] = info.el.style['background-color'] === 'yellow' ? 'black' : 'white';
  }
}
