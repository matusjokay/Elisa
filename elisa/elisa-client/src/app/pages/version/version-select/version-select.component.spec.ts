import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VersionSelectComponent } from './version-select.component';

describe('RoleSelectComponent', () => {
  let component: VersionSelectComponent;
  let fixture: ComponentFixture<VersionSelectComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VersionSelectComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VersionSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
