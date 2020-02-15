import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { startWith, map } from 'rxjs/operators';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { MatAutocomplete, MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';

@Component({
  selector: 'app-user-manager',
  templateUrl: './user-manager.component.html',
  styleUrls: ['./user-manager.component.less']
})
export class UserManagerComponent implements OnInit {

  searchForm: FormGroup;
  options = [
    { id: '1', name: 'Jano' },
    { id: '2', name: 'Fero' },
    { id: '3', name: 'Miso' }
  ];
  users: User[];
  selectedUser: User;
  selected = false;

  filteredOptions: Observable<any>;

  constructor(private fb: FormBuilder,
    private userService: UserService) { }

  ngOnInit() {
    this.searchForm = this.fb.group({
      id: ['', [Validators.required]],
      name: ['', [Validators.required]]
    });

    this.userService.getCachedAllUsers().subscribe(
      (result) => this.users = result,
      (error) => console.error('failed to fetch users')
    );

    this.filteredOptions = this.searchForm.get('name').valueChanges
      .pipe(
        startWith(''),
        map(value => value && value.length >= 2 ? this._filter(value).splice(0, 50) : [])
      );
  }

  displayFn(user: User): string {
    const titleBefore = user.title_before ? user.title_before : '';
    const titleAfter = user.title_after ? ` ${user.title_after}` : '';
    const fullName = `${titleBefore}${user.first_name} ${user.last_name}${titleAfter}`;
    return user ? fullName : '';
  }

  private _filter(value: string) {
    // const filterValue = `${value.first_name.toLowerCase()} ${value.last_name.toLowerCase()}`;
    value = value.toLowerCase();
    // return this.options.filter(option => option.name.toLowerCase().includes(filterValue));
    return this.users.filter(user => {
      const combinedFirst = `${user.first_name.toLowerCase()} ${user.last_name.toLowerCase()}`;
      const combinedSecond = `${user.last_name.toLowerCase()} ${user.first_name.toLowerCase()}`;
      if (user.first_name.toLowerCase().includes(value)
      || user.last_name.toLowerCase().includes(value)
      || combinedFirst.includes(value)
      || combinedSecond.includes(value)) {
        return true;
      }
    });
  }

  onEnter(event: string) {
    console.log('TODO: pressing enter and selecting');
    console.log(event);
  }

  onClear() {
    this.searchForm.get('name').setValue('');
    this.selected = false;
  }

  onSelectionChanged(event: MatAutocompleteSelectedEvent) {
    console.log('selected option');
    this.selectedUser = event.option.value;
    this.selected = true;
  }

  onManageClick() {
    console.log('Go to manage page');
    console.log(this.selectedUser);
  }

}
