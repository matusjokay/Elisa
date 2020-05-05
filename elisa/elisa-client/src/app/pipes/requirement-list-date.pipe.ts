import { Pipe, PipeTransform } from '@angular/core';
import { Requirement } from '../models/requirement';

@Pipe({
  name: 'requirementListDate'
})
export class RequirementListDatePipe implements PipeTransform {

  transform(requirements: Requirement[], date: string): Requirement[] {
    return requirements.filter(r => Requirement.toBasicDateFormat(r.last_updated) === date);
  }

}
