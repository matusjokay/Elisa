import { Component, OnInit, Inject, ViewChild } from '@angular/core';
import { UserService } from 'src/app/services/user.service';
import { User } from 'src/app/models/user';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { Department } from 'src/app/models/department';
import { MatRadioChange } from '@angular/material/radio';
import { UserSearchComponent } from 'src/app/common/user-search/user-search.component';

@Component({
  selector: 'app-department-user-detail',
  templateUrl: './department-user-detail.component.html',
  styleUrls: ['./department-user-detail.component.less']
})
export class DepartmentUserDetailComponent implements OnInit {

  department: Department;
  usersForAdding: User[];
  usersForRemoving: User[];
  users: User[];
  selectedUser: User;
  selected: boolean;
  loadingText: string;
  loading: boolean;
  isRemoving = false;
  employment: string;
  @ViewChild('searcher') searcher: UserSearchComponent;

  constructor(private userService: UserService,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<DepartmentUserDetailComponent>,
    private snackbar: SnackbarComponent
    ) { }

  ngOnInit(): void {
    this.department = this.data.department;
    this.fetchAllUsers();
  }

  onActionChange(event: MatRadioChange) {
    this.isRemoving = event.value;
  }

  fetchAllUsers() {
    this.onRequestSent('Fetching all possible users...');
    this.userService.getCachedAllUsers().subscribe(
      (success) => {
        this.users = success;
        this.fetchUsersForRemoving();
      }, (error) => console.error(error)
    );
  }

  fetchUsersForRemoving() {
    this.onRequestSent('Fetching users that are on this department...');
    this.userService.getUsersByDepartment(this.department).subscribe(
      (success) => {
        this.usersForRemoving = success;
        this.usersForAdding = this.users.filter(user => !success.some(u => u.id === user.id));
      }, (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  getUsersByActionType() {
    if (this.isRemoving) {
      return this.usersForRemoving;
    } else {
      return this.usersForAdding;
    }
  }

  onRequestSent(msg: string) {
    this.loadingText = msg;
    this.loading = true;
  }

  onRequestDone() {
    this.loadingText = '';
    this.loading = false;
  }

  onSelectedUser(user: User) {
    console.log(user);
    this.selectedUser = user;
  }

  onEmploymentChange(event: MatRadioChange) {
    this.employment = event.value;
  }

  onSelected(value: boolean) {
    this.selected = value;
  }

  onButtonClick() {
    if (!this.isRemoving) {
      this.onRequestSent(`Adding ${this.selectedUser.username} to ${this.department.name}...`);
      this.userService.addUserToDepartment(
        this.employment, this.department.id, this.selectedUser.id
      ).subscribe(
        (success) => {
          this.usersForRemoving = [...this.usersForRemoving, this.selectedUser];
          this.usersForAdding = this.usersForAdding.filter(user => this.selectedUser.id !== user.id);
          this.searcher.onClear();
          this.snackbar.openSnackBar(
            `Successfully added user to Department!`,
            'Close',
            this.snackbar.styles.success);
        }, (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to add user to Department!`,
            'Close',
            this.snackbar.styles.failure);
        }
      ).add(() => this.onRequestDone());
    } else {
      this.onRequestSent(`Removing ${this.selectedUser.username} from ${this.department.name}...`);
      this.userService.removeUserFromDepartment(
        this.department.id, this.selectedUser.id).subscribe(
          (success) => {
            this.usersForAdding = [...this.usersForAdding, this.selectedUser];
            this.usersForRemoving = this.usersForRemoving.filter(user => this.selectedUser.id !== user.id);
            this.searcher.onClear();
            this.snackbar.openSnackBar(
              `Successfully removed user from Department!`,
              'Close',
              this.snackbar.styles.success);
          }, (error) => {
            console.error(error);
            this.snackbar.openSnackBar(
              `Failed to remove user from Department!`,
              'Close',
              this.snackbar.styles.failure);
          }
        ).add(() => this.onRequestDone());
    }
  }

  onCloseDialog() {
    this.dialogRef.close();
  }

}
