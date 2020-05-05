import { Component, OnInit, Input, OnDestroy, Output, EventEmitter } from '@angular/core';
import { User } from 'src/app/models/user';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { startWith, map, tap } from 'rxjs/operators';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';

@Component({
  selector: 'app-user-search',
  templateUrl: './user-search.component.html',
  styleUrls: ['./user-search.component.less']
})
export class UserSearchComponent implements OnInit, OnDestroy {

  @Input()
  users: User[];
  searchForm: FormGroup;
  cacheUser: User;
  @Input()
  isDisabled: boolean;
  filteredOptions: Observable<any>;
  @Output()
  selectedUser = new EventEmitter<User>();
  @Output()
  selected = new EventEmitter<boolean>();

  constructor(private fb: FormBuilder) { }

  ngOnInit(): void {
    this.searchForm = this.fb.group({
      id: ['', [Validators.required]],
      name: ['', [Validators.required]]
    });

    this.filteredOptions = this.searchForm.get('name').valueChanges
      .pipe(
        startWith(''),
        map(value => value && value.length >= 2 ? this._filter(value).splice(0, 50) : []),
        tap(() => {
          if (this.searchForm.get('name').hasError('required') &&
              this.displayFn(this.cacheUser) !== this.searchForm.get('name').value) {
            this.selected.emit(false);
          }
        })
      );
  }

  // TODO: recreate user fetching to NOT construct fullname on client
  displayFn(user: User): string {
    if (!user) {
      return '';
    }
    const titleBefore = user.title_before ? user.title_before : '';
    const titleAfter = user.title_after ? ` ${user.title_after}` : '';
    const fullName = `${titleBefore}${user.first_name} ${user.last_name}${titleAfter}`;
    return fullName;
  }

  /**
   * Filters based on first and last name
   * without being case sensitive
   * @param value provided string in the input box
   */
  private _filter(value: string) {
    value = value.toLowerCase();
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

  onSelectionChanged(event: MatAutocompleteSelectedEvent) {
    this.selectedUser.emit(event.option.value);
    this.cacheUser = event.option.value;
    this.selected.emit(true);
  }

  onClear() {
    this.searchForm.get('name').setValue('');
    this.cacheUser = null;
    this.selected.emit(false);
  }

  onDisable(event: boolean) {
    if (event) {
      this.searchForm.get('name').disable();
    } else {
      this.searchForm.get('name').enable();
    }
  }

  ngOnDestroy() {
    console.log('destroyed search');
  }

}
