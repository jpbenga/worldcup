import { PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { WorldCupService } from '../../services/worldcup.service';

@Component({
  selector: 'app-simulation',
  imports: [PercentPipe, RouterLink],
  templateUrl: './simulation.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulationComponent {
  private readonly worldCupService = inject(WorldCupService);

  readonly vm = toSignal(this.worldCupService.getRoadToTheTrophyViewModelV2131B());
  readonly selectedGroup = signal('A');
  readonly selectedRound = signal('round_of_32');
  readonly selectedStatus = signal('all');
  readonly selectedTeam = signal<string | null>(null);
  readonly selectedMatchId = signal<string | null>(null);

  readonly activeGroup = computed(() => this.vm()?.groups.find((group: any) => group.group === this.selectedGroup()));
  readonly activeRound = computed(() => this.vm()?.rounds.find((round: any) => round.key === this.selectedRound()));
  readonly selectedMatch = computed(() =>
    this.vm()?.rounds.flatMap((round: any) => round.matches).find((match: any) => match.match_id === this.selectedMatchId()),
  );
  readonly selectedTeamPath = computed(() => this.vm()?.team_paths[this.selectedTeam() ?? ''] ?? []);

  selectTeam(team: string): void {
    this.selectedTeam.set(team);
    this.selectedMatchId.set(null);
  }

  selectMatch(match: any): void {
    this.selectedMatchId.set(match.match_id);
  }

  isHighlighted(team: string): boolean {
    return this.selectedTeam() === team;
  }

  reset(): void {
    this.selectedGroup.set('A');
    this.selectedRound.set('round_of_32');
    this.selectedStatus.set('all');
    this.selectedTeam.set(null);
    this.selectedMatchId.set(null);
  }
}
