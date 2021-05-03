select CONCAT(public.runs.job_name, ' ', public.runs.id), sum(public.steps.durationinmillis)
from public.runs
INNER JOIN public.nodes on (public.runs.run_uuid = public.nodes.run_uuid)
INNER JOIN public.steps on (public.steps.node_uuid = public.nodes.node_uuid)
where public.steps.displayname = 'Sleep'
group by public.runs.run_uuid;