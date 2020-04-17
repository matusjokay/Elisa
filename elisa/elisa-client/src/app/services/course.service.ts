import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share, distinctUntilChanged} from 'rxjs/operators';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {Course} from '../models/course';
import { IPage } from '../models/page.model';
import { BaseService } from './base-service.service';
import { CourseUser, CourseRole, CourseUserRole } from '../models/course-users.model';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getAll(pageNum: number, pageSize: number): Observable<IPage> {
    const httpParams = new HttpParams()
      .set('page', pageNum.toString())
      .set('page_size', pageSize.toString());
    const httpOptions = this.baseService.getSchemaHeader();

    return this.http.get<IPage>(environment.APIUrl + 'courses/', { params: httpParams, headers : httpOptions }).pipe(
      distinctUntilChanged(),
      share()
      );
  }

  getCoursesByTeacherMap(): Observable<Course[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Course[]>(environment.APIUrl + "teachers/", options).pipe(
      map((response: any) => {
        return response.reduce(function(r, e) {
          r[e.subject.id] = e.subject;
          r[e.subject.id]["id_teacher"] = e.user.id;
          r[e.subject.id]["teacher_name"] = e.user.fullname;
          return r;
        });
        }
      ),
      share());
  }

  getUsersBySubject(courseId: number): Observable<CourseUser[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    const params = new HttpParams().set('subject', courseId.toString());
    return this.http.get<CourseUser[]>(`${environment.APIUrl}subject-users/get_users/`,
      { headers: httpOptions, params: params });
  }

  getRolesOfUserOnCourse(courseId: number, userId: number): Observable<CourseUserRole[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    const params = new HttpParams()
      .set('subject', courseId.toString())
      .set('user', userId.toString());
    return this.http.get<CourseUserRole[]>(`${environment.APIUrl}subject-users/get_entries_user/`,
      { headers: httpOptions, params: params });
  }

  getCourseRoles(): Observable<CourseRole[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<CourseRole[]>(`${environment.APIUrl}user-subject-roles/`,
      { headers: httpOptions });
  }

  addCourseRole(userId: number, courseId: number, roleId: number): Observable<CourseUserRole> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post<CourseUserRole>(`${environment.APIUrl}subject-users/`,
      {
        user_id: userId,
        subject_id: courseId,
        role_id: roleId
      }, { headers : httpOptions }).pipe(
        map(res => {
          return { idRow: res['id'], roleId: res['role']['id'] };
        })
      );
  }

  addCourseUserRole(userId: number, courseId: number, roleId: number): Observable<CourseUser> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post<CourseUser>(`${environment.APIUrl}subject-users/`,
      {
        user_id: userId,
        subject_id: courseId,
        role_id: roleId
      }, { headers : httpOptions }).pipe(
        map(res => {
          return {
            userId: res['user']['id'], userFullname: res['user']['fullname'],
            roles: [{idRow: res['id'], roleId: res['role']['id']}], rolesAmount: 1
          };
        })
      );
  }

  deleteCourseRoleEntry(rowId: number) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.delete(`${environment.APIUrl}subject-users/${rowId}/`,
      { headers: httpOptions });
  }

  deleteUserFromCourse(userId: number, courseId: number) {
    const httpOptions = this.baseService.getSchemaHeader();
    const params = new HttpParams()
      .set('subject', courseId.toString())
      .set('user', userId.toString());
    return this.http.delete(`${environment.APIUrl}subject-users/remove_entries/`,
      { headers: httpOptions, params: params });
  }

  deleteCourse(courseId: number) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.delete(environment.APIUrl + `courses/${courseId}/`, { headers: httpOptions });
  }

  createCourse(newCourse: Course) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post<Course>(environment.APIUrl + 'courses/', newCourse, { headers: httpOptions });
  }

  updateCourse(updatedCourse: Course) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.put<Course>(environment.APIUrl + `courses/${updatedCourse.id}/`, updatedCourse, { headers : httpOptions });
  }
}
