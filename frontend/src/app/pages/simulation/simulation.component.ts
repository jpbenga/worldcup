import { AsyncPipe, DatePipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { WorldCupService } from '../../services/worldcup.service';

@Component({
  selector: 'app-simulation',
  imports: [AsyncPipe, DatePipe, PercentPipe, RouterLink],
  templateUrl: './simulation.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulationComponent {
  private readonly worldCupService = inject(WorldCupService);

  readonly simulation$ = combineLatest({
    scenario: this.worldCupService.getLivingWorldCupScenarioV213(),
    paths: this.worldCupService.getRepresentativeTournamentPathsV213(),
    creative: this.worldCupService.getCreativeTournamentExperience(),
  });

  readonly rounds = [
    { key: 'round_of_32', label: '16es', short: '16es' },
    { key: 'round_of_16', label: '8es', short: '8es' },
    { key: 'quarter_finals', label: 'Quarts', short: 'Quarts' },
    { key: 'semi_finals', label: 'Demies', short: 'Demies' },
    { key: 'final', label: 'Finale', short: 'Finale' },
  ];
}
