import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CollisionCardComponent } from './collision-card.component';

describe('CollisionCardComponent', () => {
  let component: CollisionCardComponent;
  let fixture: ComponentFixture<CollisionCardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CollisionCardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CollisionCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
