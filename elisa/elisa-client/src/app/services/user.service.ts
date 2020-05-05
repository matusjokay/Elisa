import { Injectable } from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map, share, shareReplay} from 'rxjs/operators';
import {User} from '../models/user';
import {Observable} from 'rxjs';
import { BaseService } from './base-service.service';
import { CourseRole } from '../models/course-users.model';
import { Department } from '../models/department';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private cachedUsersList$: Observable<Array<User>>;

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getAll(): Observable<User[]>{
    return this.http.get<User[]>(environment.APIUrl + 'users/').
    pipe(
      map((data: any) =>{
        return data;
        }
      ),share());
  }

  getAllMap(): Observable<User>{
    return this.http.get<User>(environment.APIUrl + 'users/').
    pipe(
      map((data: any) =>{
        return data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id].requirements = {};
          r[e.id].events = [];
          return r;
        }, {});
        }
      ),share());
  }

  getCachedAllUsers() {
    if (!this.cachedUsersList$) {
      this.cachedUsersList$ = this.requestAllUsers().pipe(
        shareReplay({
          bufferSize: 1,
          refCount: true
        })
      );
    }

    return this.cachedUsersList$;
  }

  private requestAllUsers(): Observable<User[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<User[]>(environment.APIUrl + 'users/list_all/', { headers: httpOptions });
  }

  getTeachersOrStudents(roleId: number): Observable<{userId: number}[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    const params = new HttpParams().set('role', roleId.toString());
    return this.http.get<{userId: number}[]>(`${environment.APIUrl}subject-users/filter_users_by_role`,
      { headers: httpOptions, params: params });
  }

  getUserCourseRoles(): Observable<CourseRole[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<CourseRole[]>(`${environment.APIUrl}user-subject-roles/`,
      { headers: httpOptions });
  }

  getUsersByDepartment(department: Department): Observable<User[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    let params = null;
    if (!department.parent) {
      params = new HttpParams().set('department', department.id.toString());
    } else {
      params = new HttpParams()
        .set('department', department.id.toString())
        .set('parent', department.parent.toString());
    }
    return this.http.get<User[]>(`${environment.APIUrl}user-department/get_users_by_department/`,
      { headers: httpOptions, params: params});
  }

  addUserToDepartment(employment: string, departmentId: number, userId: number) {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    const body = {
      employment: employment,
      department: departmentId,
      user: userId
    };
    return this.http.post(`${environment.APIUrl}user-department/`,
      body, { headers: httpOptions });
  }

  removeUserFromDepartment(departmentId: number, userId: number) {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    const params = new HttpParams()
      .set('department', departmentId.toString())
      .set('user', userId.toString());
    return this.http.delete(`${environment.APIUrl}user-department/remove_user_from_department`,
      { headers: httpOptions, params: params});
  }

  fetchUser(userId: number): Observable<User> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<User>(`${environment.APIUrl}users/${userId}/`,
      { headers: httpOptions });
  }

  deleteUser(user: User) {
    return this.http.delete(`${environment.APIUrl}users/${user.id}/`).
    pipe(
      map((response: any) => {
          return response;
        }
      )).subscribe();
  }

  createUser(post: any) {

  }

  updateUser(post: any) {

  }
}
