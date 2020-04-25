import { UserSearchComponent } from './../../../common/user-search/user-search.component';
import { MatSelectChange } from '@angular/material/select';
import { SpinnerComponent } from './../../../common/spinner/spinner.component';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CourseService } from './../../../services/course.service';
import { CourseUser, CourseRole } from './../../../models/course-users.model';
import { Component, OnInit, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { NgForm } from '@angular/forms';
import { tap } from 'rxjs/operators';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';

@Component({
  selector: 'app-course-teacher',
  templateUrl: './course-teacher.component.html',
  styleUrls: ['./course-teacher.component.less']
})
export class CourseTeacherComponent implements OnInit {

  users: CourseUser[];
  usersForAdding: User[];
  selectedUserForAdding: User;
  emptyUsers: boolean;
  isSelectedUser = false;
  isSelectedRole = false;
  courseChanged: boolean;
  canAdd: boolean;
  userRoles: CourseUser[];
  courseRoles: CourseRole[];
  courseId: number;
  courseName: string;
  courseTeacherId: number;
  clickBtn: boolean;
  loadingData: boolean;
  loadingAdding: boolean;
  spinnerText: string;

  constructor(private courseService: CourseService,
    private userService: UserService,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<CourseTeacherComponent>,
    private snackbar: SnackbarComponent) {
      this.fetchCourseRoles();
    }

  ngOnInit(): void {
    this.courseId = this.data.course.id;
    this.courseName = this.data.course.name;
    this.courseTeacherId = this.data.course.teacher ? this.data.course.teacher.id : null;
    this.fetchUsersOnSubject();
  }

  fetchCourseRoles() {
    this.courseService.getCourseRoles().subscribe(
      (success) => this.courseRoles = success,
      (error) => {
        console.error(error);
      }
    );
  }

  fetchUsersOnSubject() {
    this.onRequestSent('Fetching users for this subject...');
    this.courseService.getUsersBySubject(this.courseId)
      .subscribe(
      (success) => {
        // Try to create teacher entry from course data
        if (success &&
            success.length === 0 &&
            this.courseTeacherId) {
          this.addTeacherInitEntry();
        } else if (success &&
          success.length === 0 &&
          !this.courseTeacherId) {
          this.emptyUsers = true;
          this.users = success;
        } else {
          this.emptyUsers = false;
          this.users = success;
        }
      },
      (error) => {
        console.error(error);
        this.dialogRef.close(false);
      }
    ).add(() => this.loadingData = false);
  }

  addTeacherInitEntry() {
    // TODO: roleId is 2 because of 'garant' being set as teacher
    const roleId = 2;
    this.onRequestSent('Adding teacher for this subject...');
    this.courseService.addCourseUserRole(this.courseTeacherId, this.courseId, roleId)
      .subscribe(
        (success) => {
          this.courseChanged = true;
          this.emptyUsers = false;
          this.users = [success];
          this.snackbar.openSnackBar(
            `Added User ${success.userFullname} for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.success);
        },
        (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to add INIT user for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.failure);
        }
      ).add(() => this.loadingData = false);
  }

  onOpened(user: CourseUser) {
    if (!user.roles) {
      this.courseService.getRolesOfUserOnCourse(this.courseId, user.userId).subscribe(
        (success) => {
          user.roles = success;
          user.rolesAmount = success.length;
        },
        (error) => console.error(error)
      );
    }
    user.isOpened = true;
  }

  onOpenedAdding() {
    if (!this.usersForAdding) {
      this.loadingAdding = true;
      this.userService.getCachedAllUsers()
        .subscribe(
          (success: User[]) => {
            this.usersForAdding = success.filter(user => {
              return !this.users.some(courseUser => user.id === courseUser.userId);
            });
          }, (error) => {
            console.error(error);
          }
        ).add(() => this.loadingAdding = false);
    }
  }

  onRoleAddChange(event: MatSelectChange, btn: MatButton) {
    btn.disabled = event.value ? false : true;
  }

  onUserAddChange(event: MatSelectChange) {
    this.isSelectedRole = event.value ? true : false;
  }

  onRoleAdd(el: MatButton, form: NgForm, user: CourseUser, spinner: SpinnerComponent) {
    const roleId = form.value.roleSelect['id'];
    form.resetForm();
    this.onRequestSent('Add role for user...', spinner);
    this.courseService.addCourseRole(user.userId, this.courseId, roleId)
      .pipe(tap(() => spinner.hidden = true))
      .subscribe(
        (success) => {
          el.disabled = true;
          user.roles = [...user.roles, success];
          user.rolesAmount = user.roles.length;
          this.snackbar.openSnackBar(
            `Added role for ${user.userFullname}!`,
            'Close',
            this.snackbar.styles.success);
        },
        (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to add role for ${user.userFullname}!`,
            'Close',
            this.snackbar.styles.failure);
        }
      );
  }

  onUserAdd(searcher: UserSearchComponent, form: NgForm, spinner: SpinnerComponent) {
    spinner.hidden = false;
    const userIdToAdd = this.selectedUserForAdding.id;
    const roleId = form.value.roleSelectForAdd['id'];
    form.reset();
    this.courseService.addCourseUserRole(userIdToAdd, this.courseId, roleId)
      .pipe(tap(() => spinner.hidden = true))
      .subscribe(
        (success) => {
          if (this.users.length === 0) {
            this.courseChanged = true;
          }
          this.users = [...this.users, success];
          this.usersForAdding = this.usersForAdding.filter(addUser => success.userId !== addUser.id);
          this.clearSearcher(searcher);
          this.snackbar.openSnackBar(
            `Added User ${success.userFullname} for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.success);
        },
        (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to add user for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.failure);
        }
      );
  }

  clearSearcher(searcher: UserSearchComponent) {
    searcher.searchForm.get('name').setValue('');
    searcher.cacheUser = null;
    searcher.selected.emit(false);
  }

  onRequestSent(msg: string, el?: SpinnerComponent) {
    if (el) {
      el['loadingText'] = msg;
      el['hidden'] = false;
    } else {
      this.loadingData = true;
      this.spinnerText = msg;
    }
  }

  removeUser(user: CourseUser, spinner: SpinnerComponent) {
    this.clickBtn = true;
    this.onRequestSent('Removing user and its roles...', spinner);
    this.courseService.deleteUserFromCourse(user.userId, this.courseId)
      .subscribe(
        (success) => {
          if (success && success['modified']) {
            this.courseChanged = true;
          }
          this.users = this.users.filter(removedUser => user.userId !== removedUser.userId);
          this.snackbar.openSnackBar(
            `Successfully removed user ${user.userFullname} from ${this.courseName}!`,
            'Close',
            this.snackbar.styles.success);
          this.fetchAndAddUserAfterRemoval(user.userId);
        },
        (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to remove user for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.failure);
        }
      ).add(() => spinner.hidden = true);
  }

  removeRoleEntry(user: CourseUser, role: CourseRole, spinner: SpinnerComponent) {
    this.onRequestSent('Removing role from user...', spinner);
    const roleEntry = user.roles.find(userRole => role.id === userRole.roleId);
    this.courseService.deleteCourseRoleEntry(roleEntry.idRow)
      .subscribe(
        (success) => {
          if (user.rolesAmount > 1) {
            user.roles = user.roles.filter(oldRole => oldRole.idRow !== roleEntry.idRow);
            user.rolesAmount = user.roles.length;
            this.snackbar.openSnackBar(
              `Successfully removed role from ${user.userFullname} for ${this.courseName}!`,
              'Close',
              this.snackbar.styles.success);
          } else {
            if (success && success['modified']) {
              this.courseChanged = true;
            }
            this.snackbar.openSnackBar(
              `Successfully removed user ${user.userFullname} from ${this.courseName}!`,
              'Close',
              this.snackbar.styles.success);
            this.users = this.users.filter(removedUser => user.userId !== removedUser.userId);
            this.fetchAndAddUserAfterRemoval(user.userId);
          }
        }, (error) => {
          console.error(error);
          this.snackbar.openSnackBar(
            `Failed to remove role for ${this.courseName}!`,
            'Close',
            this.snackbar.styles.failure);
        }
    ).add(() => spinner.hidden = true);
  }

  fetchAndAddUserAfterRemoval(userId: number) {
    this.userService.fetchUser(userId)
      .subscribe(
        (success) => {
          if (this.usersForAdding) {
            this.usersForAdding = [...this.usersForAdding, success];
          }
        },
        (error) => {
          console.error(error);
        }
      );
  }

  onSelectedUser(user: User) {
    this.selectedUserForAdding = user;
  }

  onSelected(selected: boolean) {
    this.isSelectedUser = selected;
  }

  onCloseDialog() {
    this.dialogRef.close(this.courseChanged);
  }

}
