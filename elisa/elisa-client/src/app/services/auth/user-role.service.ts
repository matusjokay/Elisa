import { Injectable } from '@angular/core';
import { Role } from 'src/app/models/role.model';
import { BaseService } from '../base-service.service';
import { Observable } from 'rxjs';
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

}
