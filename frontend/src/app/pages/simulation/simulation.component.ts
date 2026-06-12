import { AsyncPipe, DatePipe, DecimalPipe, PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest, map } from 'rxjs';
import { TournamentGroupSimulation, TournamentTeamSimulation } from '../../models/worldcup.models';
import { WorldCupService } from '../../services/worldcup.service';

@Component({
  selector: 'app-simulation',
  imports: [AsyncPipe, DatePipe, DecimalPipe, PercentPipe, RouterLink],
  templateUrl: './simulation.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulationComponent {
  private readonly worldCupService = inject(WorldCupService);
  readonly selectedGroup = signal('Group A');
  readonly simulation$ = combineLatest({
    simulation: this.worldCupService.getConditionedTournamentSimulation(),
    campaign: this.worldCupService.getProjectedCampaign(),
  }).pipe(
    map(({ simulation, campaign }) => ({
      ...simulation,
      campaign,
      topQualification: [...simulation.teams]
        .sort((a, b) => b.qualificationProbability - a.qualificationProbability)
        .slice(0, 8),
      mostUncertain: [...simulation.teams]
        .sort(
          (a, b) =>
            Math.abs(a.qualificationProbability - 0.5) - Math.abs(b.qualificationProbability - 0.5),
        )
        .slice(0, 4),
      largestRises: simulation.largestRises.filter((item) => item[1] > 0).slice(0, 4),
      largestFalls: simulation.largestFalls.filter((item) => item[1] < 0).slice(0, 4),
    })),
  );

  groupFor(groups: TournamentGroupSimulation[], group: string): TournamentGroupSimulation | undefined {
    return groups.find((item) => item.group === group);
  }

  orderedTeams(group: TournamentGroupSimulation): TournamentTeamSimulation[] {
    return [...group.teams].sort((a, b) => b.qualificationProbability - a.qualificationProbability);
  }
}
