import { BaseService } from 'src/app/services/base-service.service';
import { Component, OnInit } from '@angular/core';
import { tap } from 'rxjs/operators';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { RoleAuth, RoleManager } from 'src/app/models/role.model';

@Component({
  selector: 'app-user-manager',
  templateUrl: './user-manager.component.html',
  styleUrls: ['./user-manager.component.less']
})
export class UserManagerComponent implements OnInit {

  users: User[];
  selectedUser: User;
  selected = false;
  manage = false;
  loading: boolean;
  authorization: RoleAuth;

  constructor(private userService: UserService,
    private baseService: BaseService) { }

  ngOnInit() {
    this.authorization = RoleManager.getRolePrivileges(this.baseService.getUserRoles());
    this.fetchAllUsers();
  }

  fetchAllUsers() {
    this.loading = true;
    this.userService.getCachedAllUsers()
      .pipe(tap(() => this.loading = false))
      .subscribe(
      (result) => this.users = result,
      (error) => console.error('failed to fetch users')
    );
  }

  onSelectedUser(user: User) {
    console.log('received user');
    console.log(user);
    this.selectedUser = user;
    this.manage = false;
  }

  onSelected(selected: boolean) {
    this.selected = selected;
  }

  onManageClick() {
    this.manage = true;
  }

  onCloseDetailHandle(value) {
    if (value) {
      this.manage = false;
    }
  }

}
