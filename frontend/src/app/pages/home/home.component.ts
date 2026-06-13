import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { DualMatrixComparison, MatchPrediction, MatchState, ModelComparison } from '../../models/worldcup.models';
import { PredictionService } from '../../services/prediction.service';
import { ResponsibleNoticeComponent } from '../../components/responsible-notice/responsible-notice.component';
import { ModelComparisonService } from '../../services/model-comparison.service';
import { WorldCupService } from '../../services/worldcup.service';
import { GroupTabsComponent } from '../../components/group-tabs/group-tabs.component';
import { MatchModalComponent } from '../../components/match-modal/match-modal.component';

@Component({
  selector: 'app-home',
  imports: [
    AsyncPipe,
    GroupTabsComponent,
    MatchModalComponent,
    ResponsibleNoticeComponent,
    RouterLink,
  ],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly predictionService = inject(PredictionService);
  private readonly modelComparisonService = inject(ModelComparisonService);
  private readonly worldCupService = inject(WorldCupService);

  readonly selectedMatchId = signal<string | null>(null);
  readonly viewModel$ = combineLatest({
    predictions: this.predictionService.getPredictions(),
    eloPredictions: this.predictionService.getEloPredictions(),
    modelComparisons: this.modelComparisonService.getComparisons(),
    groups: this.worldCupService.getGroups(),
    groupStrengths: this.worldCupService.getStrengths(),
    matchStates: this.worldCupService.getMatchStates(),
    liveStandings: this.worldCupService.getLiveGroupStandings(),
    dualMatrixComparisons: this.worldCupService.getDualMatrixComparisons(),
  });

  predictionFor(predictions: MatchPrediction[], matchId: string): MatchPrediction | undefined {
    return predictions.find((prediction) => prediction.matchId === matchId);
  }

  comparisonFor(comparisons: ModelComparison[], matchId: string): ModelComparison | undefined {
    return comparisons.find((comparison) => comparison.matchId === matchId);
  }

  matchStateFor(states: MatchState[], matchId: string): MatchState | undefined {
    return states.find((state) => state.matchId === matchId);
  }

  dualMatrixFor(comparisons: DualMatrixComparison[], matchId: string): DualMatrixComparison | undefined {
    return comparisons.find((comparison) => comparison.matchId === matchId);
  }

}
