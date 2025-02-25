import { useSettingsStore } from '@/stores/settings.store';

const DEFAULT_TITLE = 'Agentic Workflows';

export function useDocumentTitle() {
	const settingsStore = useSettingsStore();
	const { releaseChannel } = settingsStore.settings;
	const suffix =
		!releaseChannel || releaseChannel === 'stable'
			? 'Flowstate'
			: `Flowstate[${releaseChannel.toUpperCase()}]`;

	const set = (title: string) => {
		const sections = [suffix, DEFAULT_TITLE];
		document.title = sections.join(': ');
	};

	const reset = () => {
		set('');
	};

	return { set, reset };
}
