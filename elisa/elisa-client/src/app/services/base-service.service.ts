import { Injectable } from '@angular/core';
import { HttpHeaders } from '@angular/common/http';
import { UserData } from '../models/user-data';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class BaseService {

  private _access: string;
  private _userData: UserData;
  public redirectUrl: string;

  constructor() { }

  public setAccess(access: string) {
    this._access = access;
    // side effect inside setter function to setup userData
    const accessRaw = new JwtHelperService().decodeToken(this._access);
    this._userData = {
      id: Number(accessRaw.user_id),
      name: accessRaw.name,
      roles: accessRaw.roles
    };
  }

  public getAccess(): string {
    return this._access;
  }

  public getUserData(): UserData {
    return this._userData;
  }

  public getUserName(): string {
    return this._userData ? this._userData.name : null;
  }

  public getUserId(): number {
    return this._userData ? this._userData.id : null;
  }

  public getUserRoles(): number[] {
    return this._userData ? this._userData.roles : [];
  }

  public getSchemaHeader(): HttpHeaders {
    const token = this._access;
    const version = localStorage.getItem('active_scheme');
    return new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Timetable-Version': version
    });
  }

  public getAuthHeaderOnly(): HttpHeaders {
    const token = this._access;
    return new HttpHeaders({
        'Authorization': `Bearer ${token}`
    });
  }
}
