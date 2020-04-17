import { Injectable } from '@angular/core';
import { Role } from 'src/app/models/role.model';
import { BaseService } from '../base-service.service';
import { Observable } from 'rxjs';
import { Account } from '../../models/account.model';
import { environment } from 'src/environments/environment';
import { tap } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UserRoleService {

  constructor(private baseService: BaseService,
    private http: HttpClient) { }

  getLoggedUserRoles(roleIds: number[]): Observable<Role[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    const userId = this.baseService.getUserId();
    return this.http.get<Role[]>(`${environment.APIUrl}users/${userId}/get_user_roles/`,
      { headers: httpOptions }).pipe(
        tap(results => {
          results.filter(res => roleIds.includes(res.id));
        })
      );
  }

  getUserRoles(userId: number): Observable<Role[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<Role[]>(`${environment.APIUrl}users/${userId}/get_user_roles/`,
      { headers: httpOptions });
  }

  updateUserRoles(userId: number, roles: Role[]): Observable<string> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.put<string>(`${environment.APIUrl}users/${userId}/update_roles/`,
      roles,
      { headers: httpOptions });
  }

  setInitUserRoles(account: Account, userId: number): Observable<any> {
    const loginData = {
      'username': account.username,
      'password': account.password
    };
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.put(`${environment.APIUrl}users/${userId}/set_user_init_roles/`,
      loginData, { headers: httpOptions , withCredentials: true}
    ).pipe(
      tap((response: any) => {
        if ((typeof response === 'string' || response instanceof String)) {
          return;
        }
        this.baseService.setAccess(response.access);
      }
    ));
  }

}
