select  public.nodes.displayname, public.nodes.node_uuid, sum(public.steps.durationinmillis) as duration
from public.nodes
INNER JOIN public.steps on (public.steps.node_uuid = public.nodes.node_uuid)
where public.steps.displayname = 'Sleep'
group by public.nodes.node_uuid
order by duration
desc;