import { AsyncPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { DataSourceInfo, DataSourcesSnapshot, Match, MatchPrediction, ModelComparison, PredictionEvaluation, ReleaseCandidatePrediction, WorldCupResult } from '../../models/worldcup.models';
import { BacktestingService } from '../../services/backtesting.service';
import { MatchService } from '../../services/match.service';
import { PredictionService } from '../../services/prediction.service';
import { PredictionHistoryComponent } from '../../components/prediction-history/prediction-history.component';
import { ResponsibleNoticeComponent } from '../../components/responsible-notice/responsible-notice.component';
import { DataSourceBadgeComponent } from '../../components/data-source-badge/data-source-badge.component';
import { DataSourceService } from '../../services/data-source.service';
import { ModelComparisonService } from '../../services/model-comparison.service';
import { WorldCupService } from '../../services/worldcup.service';
import { GroupTabsComponent } from '../../components/group-tabs/group-tabs.component';
import { MatchModalComponent } from '../../components/match-modal/match-modal.component';

@Component({
  selector: 'app-home',
  imports: [
    AsyncPipe,
    DatePipe,
    DataSourceBadgeComponent,
    GroupTabsComponent,
    MatchModalComponent,
    PredictionHistoryComponent,
    ResponsibleNoticeComponent,
    RouterLink,
  ],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly matchService = inject(MatchService);
  private readonly predictionService = inject(PredictionService);
  private readonly backtestingService = inject(BacktestingService);
  private readonly dataSourceService = inject(DataSourceService);
  private readonly modelComparisonService = inject(ModelComparisonService);
  private readonly worldCupService = inject(WorldCupService);

  readonly selectedMatchId = signal<string | null>(null);
  readonly viewModel$ = combineLatest({
    matches: this.matchService.getMatches(),
    predictions: this.predictionService.getPredictions(),
    releasePredictions: this.predictionService.getReleaseCandidatePredictions(),
    eloPredictions: this.predictionService.getEloPredictions(),
    backtests: this.backtestingService.getResults(),
    dataSources: this.dataSourceService.getSnapshot(),
    acquisitionStatus: this.dataSourceService.getAcquisitionStatus(),
    teamMappingStatus: this.dataSourceService.getTeamMappingStatus(),
    modelComparisons: this.modelComparisonService.getComparisons(),
    groups: this.worldCupService.getGroups(),
    groupStrengths: this.worldCupService.getStrengths(),
    results: this.worldCupService.getResults(),
    predictionEvaluations: this.worldCupService.getPredictionEvaluations(),
  });

  matchFor(matches: Match[], matchId: string): Match | undefined {
    return matches.find((match) => match.id === matchId);
  }

  predictionFor(predictions: MatchPrediction[], matchId: string): MatchPrediction | undefined {
    return predictions.find((prediction) => prediction.matchId === matchId);
  }

  comparisonFor(comparisons: ModelComparison[], matchId: string): ModelComparison | undefined {
    return comparisons.find((comparison) => comparison.matchId === matchId);
  }

  releasePredictionFor(predictions: ReleaseCandidatePrediction[], matchId: string): ReleaseCandidatePrediction | undefined {
    return predictions.find((prediction) => prediction.matchId === matchId);
  }

  resultFor(results: WorldCupResult[], matchId: string): WorldCupResult | undefined {
    return results.find((result) => result.matchId === matchId);
  }

  evaluationFor(evaluations: PredictionEvaluation[], matchId: string): PredictionEvaluation | undefined {
    return evaluations.find((evaluation) => evaluation.matchId === matchId);
  }

  primarySource(snapshot: DataSourcesSnapshot): DataSourceInfo | undefined {
    return snapshot.sources.find((source) => source.id === 'active_matches');
  }
}
