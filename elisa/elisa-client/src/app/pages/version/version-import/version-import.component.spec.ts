import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VersionImportComponent } from './version-import.component';

describe('VersionImportComponent', () => {
  let component: VersionImportComponent;
  let fixture: ComponentFixture<VersionImportComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VersionImportComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VersionImportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
