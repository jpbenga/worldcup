import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { DataSourceType } from '../../models/worldcup.models';

@Component({
  selector: 'app-data-source-badge',
  templateUrl: './data-source-badge.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DataSourceBadgeComponent {
  @Input({ required: true }) sourceType!: DataSourceType;
  @Input({ required: true }) isRealData = false;

  label(): string {
    if (this.isRealData || this.sourceType === 'api') {
      return 'Données réelles';
    }
    if (this.sourceType === 'generated') {
      return 'Données générées';
    }
    if (this.sourceType === 'evaluated') {
      return 'Données évaluées';
    }
    return 'Données démo';
  }

  badgeClass(): string {
    if (this.isRealData || this.sourceType === 'api') {
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300';
    }
    if (this.sourceType === 'generated') {
      return 'border-sky-500/30 bg-sky-500/10 text-sky-300';
    }
    if (this.sourceType === 'evaluated') {
      return 'border-violet-500/30 bg-violet-500/10 text-violet-300';
    }
    return 'border-amber-500/30 bg-amber-500/10 text-amber-300';
  }
}
