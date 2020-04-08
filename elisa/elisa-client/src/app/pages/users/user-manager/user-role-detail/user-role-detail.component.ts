import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { User } from 'src/app/models/user';
import { MatSelectChange } from '@angular/material/select';
import { Role, RoleManager } from 'src/app/models/role.model';
import { BaseService } from 'src/app/services/base-service.service';
import { UserRoleService } from 'src/app/services/auth/user-role.service';
import * as _ from 'lodash';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-user-role-detail',
  templateUrl: './user-role-detail.component.html',
  styleUrls: ['./user-role-detail.component.less']
})
export class UserRoleDetailComponent implements OnInit {

  @Input()
  user: User;
  selectedRoles: Role[];
  availableRoles: Role[];
  userRoles: Role[];
  changed: boolean;
  loading = false;
  snackbarMsg: string;

  @Output()
  closeMe: EventEmitter<any> = new EventEmitter<any>();

  constructor(private baseService: BaseService,
    private userRoleService: UserRoleService,
    private snackBar: SnackbarComponent) { }

  ngOnInit(): void {
    this.availableRoles = RoleManager.getRoleObjects(this.baseService.getUserRoles());
    this.loadUserRoles();
  }

  /**
   * Loads user roles on initialization
   */
  loadUserRoles() {
    this.updateLoadingText('Fetching User roles...');
    this.userRoleService.getUserRoles(this.user.id).subscribe(
      (success) => {
        this.userRoles = success;
        this.selectedRoles = success;
        this.changed = false;
      },
      (error) => {
        console.error(error);
      }
    ).add(
      () => this.updateLoadingText()
    );
  }

  updateLoadingText(msg?: string) {
    this.loading = !this.loading;
    this.snackbarMsg = msg ? msg : '';
  }

  /**
   * Compares selectedRoles againts availableRoles
   */
  compareWithFn(item1, item2) {
    return item1 && item2 ? item1.id === item2.id : item1 === item2;
  }

  checkChange(): void {
    this.changed =  !_.isEqual(this.selectedRoles, this.userRoles);
  }

  /**
   * Handler function to update current
   * status of selectedRoles and changes of
   * the previous state of userRoles
   */
  onRolesSelect(event: MatSelectChange) {
    this.selectedRoles = event.value;
    this.checkChange();
  }

  /**
   * Updates roles for particular user
   * by selectedRoles array.
   */
  onUpdate() {
    this.updateLoadingText('Updating roles for user...');
    this.userRoleService.updateUserRoles(this.user.id, this.selectedRoles)
      .subscribe(
        (success) => {
          this.snackBar.openSnackBar(`Roles successfully updated for ${this.user.username}!`,
          'Close',
          this.snackBar.styles.success);
          this.userRoles = _.cloneDeep(this.selectedRoles);
        },
        (error) => {
          catchError(error);
          this.snackBar.openSnackBar(`Error during roles updating!`,
          'Close',
          this.snackBar.styles.failure);
        }
      ).add(
        () => {
          this.checkChange();
          this.updateLoadingText();
        }
      );
  }

  /**
   * Helper function to call parents
   * handler function to destroy this component.
   */
  onClose(): void {
    this.closeMe.emit(true);
  }

}
