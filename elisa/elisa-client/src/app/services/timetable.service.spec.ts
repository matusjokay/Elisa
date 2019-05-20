import { TestBed } from '@angular/core/testing';

import { TimetableService } from './timetable.service';

describe('TimetableService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: TimetableService = TestBed.get(TimetableService);
    expect(service).toBeTruthy();
  });
});
