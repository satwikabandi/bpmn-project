import React, { useState, useEffect, useRef } from 'react';
import BpmnNavigatedViewer from 'bpmn-js/lib/NavigatedViewer';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Send, FileText, Activity, Upload, Paperclip, ZoomIn, ZoomOut, RotateCcw, Map, List, Download, Edit2, Check, X, RefreshCw } from 'lucide-react';

// Premium styled TreeNode component with dark theme
const TreeNode = ({ node }) => {
    if (!node) return null;
    if (node.error) {
        return <div style={{
            color: '#ef4444',
            padding: '1.5rem',
            background: 'rgba(239, 68, 68, 0.1)',
            borderRadius: '12px',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            backdropFilter: 'blur(10px)'
        }}>{node.error}</div>;
    }

    if (node.isHidden) {
        return (
            <>
                {node.children.map(child => <TreeNode key={child.id} node={child} />)}
                {node.continuation && <TreeNode node={node.continuation} />}
            </>
        );
    }

    const type = node.type || 'Node';
    const name = node.name || '';
    const localName = node.localName || type.toLowerCase().replace(' ', '');
    const isSplit = node.children && node.children.length > 1;

    // Premium color schemes based on type
    const getNodeStyle = () => {
        const isStart = localName.includes('start');
        const isGateway = type === 'Gateway';

        if (isStart) {
            return {
                background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(6, 182, 212, 0.08) 100%)',
                border: '2px solid rgba(6, 182, 212, 0.6)',
                boxShadow: '0 0 20px rgba(6, 182, 212, 0.3), 0 8px 32px rgba(0, 0, 0, 0.3)',
                accentColor: '#06b6d4',
                textColor: '#67e8f9'
            };
        }
        if (localName.includes('end')) {
            return {
                background: 'linear-gradient(135deg, rgba(100, 116, 139, 0.15) 0%, rgba(100, 116, 139, 0.08) 100%)',
                border: '2px solid rgba(148, 163, 184, 0.5)',
                boxShadow: '0 0 15px rgba(100, 116, 139, 0.2), 0 8px 32px rgba(0, 0, 0, 0.3)',
                accentColor: '#94a3b8',
                textColor: '#cbd5e1'
            };
        }
        if (isGateway) {
            return {
                background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.18) 0%, rgba(168, 85, 247, 0.08) 100%)',
                border: '2px solid rgba(168, 85, 247, 0.6)',
                boxShadow: '0 0 25px rgba(168, 85, 247, 0.35), 0 8px 32px rgba(0, 0, 0, 0.3)',
                accentColor: '#a855f7',
                textColor: '#e9d5ff'
            };
        }
        // Default: Activity/Task - Blue
        return {
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%)',
            border: '2px solid rgba(59, 130, 246, 0.5)',
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.25), 0 8px 32px rgba(0, 0, 0, 0.3)',
            accentColor: '#3b82f6',
            textColor: '#bfdbfe'
        };
    };

    const nodeStyle = getNodeStyle();

    // Detect language from text (Telugu, Tamil, or English)
    const detectLanguage = (text) => {
        if (!text) return 'en';
        // Telugu Unicode range: \u0C00-\u0C7F
        if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
        // Tamil Unicode range: \u0B80-\u0BFF
        if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
        return 'en';
    };

    // Get descriptive category based on activity name keywords
    const getActivityCategory = (activityName, nodeType) => {
        if (!activityName || nodeType !== 'Activity') return '';
        const lowerName = activityName.toLowerCase();
        const lang = detectLanguage(activityName);

        // Category labels by language
        const labels = {
            userInput: { en: 'User Input', te: 'వినియోగదారు ఇన్‌పుట్', ta: 'பயனர் உள்ளீடு' },
            validation: { en: 'Validation', te: 'ధృవీకరణ', ta: 'சரிபார்ப்பு' },
            systemOutput: { en: 'System Output', te: 'వ్యవస్థ అవుట్‌పుట్', ta: 'வெளியீடு' },
            errorHandling: { en: 'Error Handling', te: 'దోష నిర్వహణ', ta: 'பிழை கையாளுதல்' },
            success: { en: 'Success', te: 'విజయం', ta: 'வெற்றி' },
            navigation: { en: 'Navigation', te: 'నావిగేషన్', ta: 'வழிசெலுத்தல்' },
            notification: { en: 'Notification', te: 'నోటిఫికేషన్', ta: 'அறிவிப்பு' },
            dataOperation: { en: 'Data Operation', te: 'డేటా ఆపరేషన్', ta: 'தரவு செயல்பாடு' },
            authentication: { en: 'Authentication', te: 'ప్రమాణీకరణ', ta: 'அங்கீகாரம்' },
            retry: { en: 'Retry', te: 'మళ్ళీ ప్రయత్నం', ta: 'மீண்டும் முயற்சி' },
            processing: { en: 'Processing', te: 'ప్రాసెసింగ్', ta: 'செயலாக்கம்' },
            task: { en: 'Task', te: 'టాస్క్', ta: 'பணி' }
        };

        // User Input related
        if (lowerName.includes('enter') || lowerName.includes('input') || lowerName.includes('submit') ||
            lowerName.includes('fill') || lowerName.includes('provide') || lowerName.includes('type') ||
            lowerName.includes('నమోదు') || lowerName.includes('టైప్') || lowerName.includes('ఇవ్వు') ||
            lowerName.includes('உள்ளிடு') || lowerName.includes('தட்டச்சு') || lowerName.includes('சமர்ப்பி')) {
            return labels.userInput[lang];
        }
        // Validation/Check
        if (lowerName.includes('validate') || lowerName.includes('check') || lowerName.includes('verify') ||
            lowerName.includes('review') || lowerName.includes('confirm') || lowerName.includes('authenticate') ||
            lowerName.includes('ధృవీకరించు') || lowerName.includes('తనిఖీ') || lowerName.includes('పరిశీలించు') ||
            lowerName.includes('சரிபார்') || lowerName.includes('சோதி') || lowerName.includes('உறுதிசெய்')) {
            return labels.validation[lang];
        }
        // Display/Show
        if (lowerName.includes('show') || lowerName.includes('display') || lowerName.includes('view') ||
            lowerName.includes('present') || lowerName.includes('open') ||
            lowerName.includes('చూపించు') || lowerName.includes('ప్రదర్శించు') || lowerName.includes('తెరువు') ||
            lowerName.includes('காட்டு') || lowerName.includes('திற') || lowerName.includes('காண்பி')) {
            return labels.systemOutput[lang];
        }
        // Error handling
        if (lowerName.includes('error') || lowerName.includes('fail') || lowerName.includes('reject') ||
            lowerName.includes('deny') || lowerName.includes('invalid') ||
            lowerName.includes('దోషం') || lowerName.includes('విఫలం') || lowerName.includes('తిరస్కరించు') ||
            lowerName.includes('பிழை') || lowerName.includes('தோல்வி') || lowerName.includes('நிராகரி')) {
            return labels.errorHandling[lang];
        }
        // Success/Completion
        if (lowerName.includes('success') || lowerName.includes('complete') || lowerName.includes('approve') ||
            lowerName.includes('accept') || lowerName.includes('grant') ||
            lowerName.includes('విజయం') || lowerName.includes('పూర్తి') || lowerName.includes('ఆమోదించు') ||
            lowerName.includes('வெற்றி') || lowerName.includes('முடிவு') || lowerName.includes('ஏற்கவும்')) {
            return labels.success[lang];
        }
        // Navigation
        if (lowerName.includes('redirect') || lowerName.includes('navigate') || lowerName.includes('go to') ||
            lowerName.includes('dashboard') || lowerName.includes('page') || lowerName.includes('screen') ||
            lowerName.includes('వెళ్ళు') || lowerName.includes('నావిగేట్') || lowerName.includes('పేజీ') ||
            lowerName.includes('செல்') || lowerName.includes('திருப்பு') || lowerName.includes('பக்கம்')) {
            return labels.navigation[lang];
        }
        // Notification
        if (lowerName.includes('send') || lowerName.includes('notify') || lowerName.includes('email') ||
            lowerName.includes('message') || lowerName.includes('alert') ||
            lowerName.includes('పంపు') || lowerName.includes('తెలియజేయు') || lowerName.includes('సందేశం') ||
            lowerName.includes('அனுப்பு') || lowerName.includes('தெரிவி') || lowerName.includes('செய்தி')) {
            return labels.notification[lang];
        }
        // Data operations
        if (lowerName.includes('save') || lowerName.includes('store') || lowerName.includes('update') ||
            lowerName.includes('delete') || lowerName.includes('fetch') || lowerName.includes('load') ||
            lowerName.includes('database') || lowerName.includes('record') ||
            lowerName.includes('సేవ్') || lowerName.includes('నిల్వ') || lowerName.includes('అప్డేట్') || lowerName.includes('తొలగించు') ||
            lowerName.includes('சேமி') || lowerName.includes('புதுப்பி') || lowerName.includes('நீக்கு')) {
            return labels.dataOperation[lang];
        }
        // Login/Authentication
        if (lowerName.includes('login') || lowerName.includes('log in') || lowerName.includes('logout') ||
            lowerName.includes('sign') || lowerName.includes('register') || lowerName.includes('session') ||
            lowerName.includes('లాగిన్') || lowerName.includes('లాగౌట్') || lowerName.includes('నమోదు') ||
            lowerName.includes('உள்நுழை') || lowerName.includes('வெளியேறு') || lowerName.includes('பதிவு')) {
            return labels.authentication[lang];
        }
        // Retry
        if (lowerName.includes('retry') || lowerName.includes('again') || lowerName.includes('repeat') ||
            lowerName.includes('resubmit') ||
            lowerName.includes('మళ్ళీ') || lowerName.includes('ప్రయత్నించు') ||
            lowerName.includes('மீண்டும்') || lowerName.includes('முயற்சி')) {
            return labels.retry[lang];
        }
        // Process/Calculate
        if (lowerName.includes('process') || lowerName.includes('calculate') || lowerName.includes('generate') ||
            lowerName.includes('create') || lowerName.includes('build') ||
            lowerName.includes('ప్రాసెస్') || lowerName.includes('లెక్కించు') || lowerName.includes('సృష్టించు') ||
            lowerName.includes('செயலாக்கு') || lowerName.includes('கணக்கிடு') || lowerName.includes('உருவாக்கு')) {
            return labels.processing[lang];
        }
        return labels.task[lang];
    };

    const activityCategory = getActivityCategory(name, type);
    const typeLabel = type === 'Activity' && activityCategory
        ? `${type.toUpperCase()} (${activityCategory})`
        : type.toUpperCase();

    // Get description for gateway based on condition
    const getGatewayDescription = (gatewayName) => {
        if (!gatewayName) return 'Decision Point';
        const lowerName = gatewayName.toLowerCase();
        const lang = detectLanguage(gatewayName);

        const labels = {
            validation: { en: 'Validation Check', te: 'ధృవీకరణ తనిఖీ', ta: 'சரிபார்ப்பு' },
            approval: { en: 'Approval Decision', te: 'ఆమోద నిర్ణయం', ta: 'ஒப்புதல் முடிவு' },
            existence: { en: 'Existence Check', te: 'ఉనికి తనిఖీ', ta: 'இருப்பு சோதனை' },
            success: { en: 'Success Check', te: 'విజయ తనిఖీ', ta: 'வெற்றி சோதனை' },
            auth: { en: 'Auth Status', te: 'ప్రమాణీకరణ స్థితి', ta: 'அங்கீகார நிலை' },
            decision: { en: 'Decision Point', te: 'నిర్ణయ స్థానం', ta: 'முடிவு புள்ளி' }
        };

        if (lowerName.includes('valid') || lowerName.includes('correct') ||
            lowerName.includes('చెల్లుబాటు') || lowerName.includes('సరైన') ||
            lowerName.includes('செல்லுபடி') || lowerName.includes('சரியான')) {
            return labels.validation[lang];
        }
        if (lowerName.includes('approve') || lowerName.includes('accept') ||
            lowerName.includes('ఆమోదం') || lowerName.includes('ఆమోదించు') ||
            lowerName.includes('ஒப்புதல்') || lowerName.includes('ஏற்கவும்')) {
            return labels.approval[lang];
        }
        if (lowerName.includes('exist') || lowerName.includes('found') ||
            lowerName.includes('ఉనికి') || lowerName.includes('కనుగొన') ||
            lowerName.includes('இருப்பு') || lowerName.includes('கண்டறிந்த')) {
            return labels.existence[lang];
        }
        if (lowerName.includes('success') || lowerName.includes('complete') ||
            lowerName.includes('విజయం') || lowerName.includes('పూర్తి') ||
            lowerName.includes('வெற்றி') || lowerName.includes('முடிவு')) {
            return labels.success[lang];
        }
        if (lowerName.includes('auth') || lowerName.includes('login') ||
            lowerName.includes('లాగిన్') || lowerName.includes('ప్రమాణీకరణ') ||
            lowerName.includes('உள்நுழை') || lowerName.includes('அங்கீகாரம்')) {
            return labels.auth[lang];
        }
        return labels.decision[lang];
    };

    const displayType = type === 'Gateway'
        ? `GATEWAY (${getGatewayDescription(name)})`
        : typeLabel;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {/* Premium Connector Line with Label */}
            {node.incomingLabel && (
                <div style={{ position: 'relative', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{
                        height: '100%',
                        width: '2px',
                        background: 'linear-gradient(180deg, rgba(100, 116, 139, 0.3), rgba(100, 116, 139, 0.8))',
                        boxShadow: '0 0 8px rgba(100, 116, 139, 0.3)'
                    }}></div>
                    <div style={{
                        position: 'absolute',
                        background: 'rgba(15, 23, 42, 0.95)',
                        backdropFilter: 'blur(8px)',
                        padding: '4px 12px',
                        fontSize: '0.7rem',
                        fontWeight: '600',
                        color: '#94a3b8',
                        border: '1px solid rgba(100, 116, 139, 0.3)',
                        borderRadius: '20px',
                        top: '-12px',
                        whiteSpace: 'nowrap',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                    }}>
                        {node.incomingLabel}
                    </div>
                </div>
            )}

            {/* Premium Node Card */}
            <div style={{
                padding: '1rem 1.5rem',
                background: nodeStyle.background,
                backdropFilter: 'blur(12px)',
                border: nodeStyle.border,
                borderRadius: '16px',
                textAlign: 'center',
                minWidth: '220px',
                maxWidth: '320px',
                boxShadow: nodeStyle.boxShadow,
                transition: 'all 0.3s ease',
                cursor: 'default'
            }}>
                <div style={{
                    fontSize: '0.6rem',
                    fontWeight: '700',
                    color: nodeStyle.accentColor,
                    textTransform: 'uppercase',
                    marginBottom: '0.4rem',
                    letterSpacing: '0.08em',
                    opacity: 0.9
                }}>{displayType}</div>
                <div style={{
                    fontWeight: '600',
                    color: nodeStyle.textColor,
                    fontSize: '0.95rem',
                    lineHeight: '1.4',
                    textShadow: '0 1px 3px rgba(0, 0, 0, 0.3)'
                }}>{name}</div>
            </div>

            {(node.children && (node.children.length > 0 || node.continuation)) && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                    {/* Connector with gradient */}
                    <div style={{
                        height: '35px',
                        width: '2px',
                        background: 'linear-gradient(180deg, rgba(100, 116, 139, 0.8), rgba(100, 116, 139, 0.3))',
                        boxShadow: '0 0 8px rgba(100, 116, 139, 0.2)'
                    }}></div>
                    {isSplit ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <div style={{
                                display: 'flex',
                                gap: '3rem',
                                borderTop: '2px solid rgba(100, 116, 139, 0.4)',
                                paddingTop: '1.5rem',
                                position: 'relative',
                                borderBottom: node.continuation ? '2px solid rgba(100, 116, 139, 0.4)' : 'none',
                                paddingBottom: node.continuation ? '1.5rem' : '0'
                            }}>
                                {node.children.map((child, i) => (
                                    <div key={child.id || i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                        <TreeNode node={child} />
                                        {node.continuation && (
                                            <div style={{
                                                height: '1.5rem',
                                                width: '2px',
                                                background: 'linear-gradient(180deg, rgba(100, 116, 139, 0.8), rgba(100, 116, 139, 0.3))'
                                            }}></div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        node.children.map((child, i) => <TreeNode key={child.id || i} node={child} />)
                    )}
                    {node.continuation && (
                        <>
                            <div style={{
                                height: '25px',
                                width: '2px',
                                background: 'linear-gradient(180deg, rgba(100, 116, 139, 0.3), rgba(100, 116, 139, 0.8))'
                            }}></div>
                            <TreeNode node={node.continuation} />
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

const ProcessFlowRenderer = ({ xml, zoomLevel = 1 }) => {

    const [tree, setTree] = useState(null);

    useEffect(() => {
        if (!xml) return;

        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, "text/xml");

            // Check for parse errors
            const parserError = doc.getElementsByTagName("parsererror");
            if (parserError.length > 0) {
                setTree({ error: "XML Parsing Error: " + parserError[0].textContent });
                return;
            }

            // Helper to find elements regardless of namespace prefix
            const getElementsByType = (typeSuffix) => {
                let results = [];
                const BPMN_NS = 'http://www.omg.org/spec/BPMN/20100524/MODEL';

                // 1. Try getElementsByTagNameNS (proper namespace handling)
                try {
                    results = Array.from(doc.getElementsByTagNameNS(BPMN_NS, typeSuffix));
                } catch { /* Ignore errors */ }
                if (results.length > 0) return results;

                // 2. Try explicit namespaced tag
                try { results = Array.from(doc.getElementsByTagName('bpmn:' + typeSuffix)); } catch { /* Ignore errors */ }
                if (results.length > 0) return results;

                // 3. Try without prefix
                try { results = Array.from(doc.getElementsByTagName(typeSuffix)); } catch { /* Ignore errors */ }
                if (results.length > 0) return results;

                // 4. Fallback: Scan all elements and match by local name
                const all = Array.from(doc.getElementsByTagName('*'));
                return all.filter(el => {
                    // Safe access to nodeName/localName
                    const nn = el.nodeName || "";
                    const ln = el.localName || nn.split(':').pop() || "";
                    return ln.toLowerCase() === typeSuffix.toLowerCase();
                });
            };

            const getElement = (id) => {
                if (!id) return null;
                // Try explicit ID first
                let el = doc.getElementById(id);
                if (el) return el;
                // Fallback scan
                const all = doc.getElementsByTagName('*');
                for (let i = 0; i < all.length; i++) {
                    if (all[i].getAttribute('id') === id) return all[i];
                }
                return null;
            };

            const allFlows = getElementsByType('sequenceFlow');

            const getOutgoingFlows = (nodeId) => {
                return allFlows
                    .filter(f => f.getAttribute('sourceRef') === nodeId)
                    .map(f => ({
                        id: f.getAttribute('id'),
                        targetRef: f.getAttribute('targetRef'),
                        name: f.getAttribute('name')
                    }));
            };

            const getOutgoingNodes = (nodeId) => getOutgoingFlows(nodeId).map(f => f.targetRef);

            const getIncomingCount = (nodeId) => {
                return allFlows.filter(f => f.getAttribute('targetRef') === nodeId).length;
            };

            const getReachable = (startId) => {
                const visited = new Set();
                const queue = [startId];
                const reachable = new Set();
                while (queue.length > 0) {
                    const curr = queue.shift();
                    if (visited.has(curr)) continue;
                    visited.add(curr);
                    reachable.add(curr);

                    const nexts = getOutgoingNodes(curr);
                    for (const n of nexts) queue.push(n);
                }
                return reachable;
            };

            const findConvergenceNode = (branchStartIds) => {
                if (!branchStartIds || branchStartIds.length < 2) return null;
                const reachableSets = branchStartIds.map(id => getReachable(id));
                if (reachableSets.length === 0) return null;

                const intersection = [...reachableSets[0]].filter(x => reachableSets.every(s => s.has(x)));
                if (intersection.length === 0) return null;

                const queue = [branchStartIds[0]];
                const visited = new Set();
                while (queue.length > 0) {
                    const curr = queue.shift();
                    if (visited.has(curr)) continue;
                    visited.add(curr);
                    if (intersection.includes(curr)) return curr;
                    const nexts = getOutgoingNodes(curr);
                    for (const n of nexts) queue.push(n);
                }
                return null;
            };

            const traverse = (elementId, stopAtId = null, visited = new Set(), incomingLabel = '') => {
                if (!elementId || visited.has(elementId)) return null;
                if (elementId === stopAtId) return null;
                if (visited.size > 100) return null; // Circuit break for infinite recursion

                visited.add(elementId);
                const element = getElement(elementId);
                if (!element) return null;

                const nn = element.nodeName || "";
                const localName = (element.localName || nn.split(':').pop() || "").toLowerCase();
                const name = element.getAttribute('name') || '';
                const incomingCount = getIncomingCount(elementId);

                let type = 'Node';
                if (localName.includes('task')) type = 'Activity';
                else if (localName.includes('gateway')) type = 'Gateway';
                else if (localName.includes('startevent')) type = 'Start Event';
                else if (localName.includes('endevent')) type = 'End Event';

                const isStructuralMerge = (type === 'Gateway' && incomingCount > 1 && !name);

                const node = {
                    id: elementId,
                    type,
                    name: name || (isStructuralMerge ? 'Merge' : (type === 'Start Event' ? 'Start' : type === 'End Event' ? 'End' : 'Step')),
                    localName,
                    children: [],
                    continuation: null,
                    isHidden: isStructuralMerge,
                    incomingLabel
                };

                const flows = getOutgoingFlows(elementId);
                const outgoingIds = flows.map(f => f.targetRef);

                if (outgoingIds.length > 0) {
                    if (outgoingIds.length > 1) {
                        const mergeNoteId = findConvergenceNode(outgoingIds);
                        // Pass a COPY of visited to branches to allow them to traverse independently until merge
                        // Actually, for strict tree, visited should prevent cycles.
                        // But shared nodes (merges) should be stopped at.
                        node.children = flows.map(flow => traverse(flow.targetRef, mergeNoteId || stopAtId, new Set(visited), flow.name)).filter(n => n !== null);
                        if (mergeNoteId) {
                            node.continuation = traverse(mergeNoteId, stopAtId, visited);
                        }
                    } else {
                        const flow = flows[0];
                        const nextNode = traverse(flow.targetRef, stopAtId, visited, flow.name);
                        if (nextNode) node.children = [nextNode];
                    }
                }

                return node;
            };

            const startEvents = getElementsByType('startEvent');
            console.log("XML length:", xml?.length, "StartEvents found:", startEvents.length);
            if (startEvents.length === 0) {
                console.log("XML content sample:", xml?.substring(0, 500));
                // Try to find any events
                const allEvents = doc.getElementsByTagName('*');
                const eventTags = Array.from(allEvents).filter(el =>
                    el.nodeName.toLowerCase().includes('event') || el.localName?.toLowerCase().includes('event')
                );
                console.log("Event-like tags found:", eventTags.map(e => e.nodeName));
            }
            if (startEvents.length > 0) {
                const root = traverse(startEvents[0].getAttribute('id'));
                if (root) {
                    setTree(root);
                } else {
                    setTree({ error: "Could not traverse process tree (Traversal returned null)." });
                }
            } else {
                console.warn("No start event found in XML");
                setTree({ error: "No start event found in generated BPMN." });
            }
        } catch (err) {
            console.error("ProcessFlowRenderer Error:", err);
            setTree({ error: "Display Error: " + err.message });
        }

    }, [xml]);

    if (!xml) return <div className="text-slate-400 text-center mt-10">No process flow to display.</div>;

    return (
        <div style={{
            padding: '2rem',
            height: '100%',
            overflowY: 'auto',
            background: 'linear-gradient(180deg, #0f172a 0%, #020617 100%)'
        }}>
            {/* Premium Title */}
            <h3 style={{
                fontSize: '1.1rem',
                fontWeight: '700',
                marginBottom: '1.5rem',
                color: '#e2e8f0',
                letterSpacing: '0.02em',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem'
            }}>
                <span style={{
                    width: '4px',
                    height: '20px',
                    background: 'linear-gradient(180deg, #3b82f6, #a855f7)',
                    borderRadius: '2px'
                }}></span>
                Process Flow Visualization
            </h3>

            {/* Premium Legend / Key with glassmorphism */}
            <div style={{
                marginBottom: '2rem',
                padding: '1.25rem',
                background: 'rgba(30, 41, 59, 0.6)',
                backdropFilter: 'blur(12px)',
                borderRadius: '16px',
                border: '1px solid rgba(100, 116, 139, 0.2)',
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
            }}>
                <h4 style={{
                    fontSize: '0.7rem',
                    fontWeight: '700',
                    color: '#64748b',
                    marginBottom: '1rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em'
                }}>Element Types</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.25rem' }}>
                    {/* Event */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                            width: '16px',
                            height: '16px',
                            borderRadius: '50%',
                            background: 'rgba(6, 182, 212, 0.15)',
                            border: '2px solid #06b6d4',
                            boxShadow: '0 0 10px rgba(6, 182, 212, 0.4)'
                        }}></div>
                        <div>
                            <span style={{ fontWeight: '600', fontSize: '0.85rem', color: '#e2e8f0' }}>Event</span>
                            <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>Start / End points</p>
                        </div>
                    </div>
                    {/* Activity */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                            width: '16px',
                            height: '12px',
                            borderRadius: '4px',
                            background: 'rgba(59, 130, 246, 0.15)',
                            border: '2px solid #3b82f6',
                            boxShadow: '0 0 10px rgba(59, 130, 246, 0.4)'
                        }}></div>
                        <div>
                            <span style={{ fontWeight: '600', fontSize: '0.85rem', color: '#e2e8f0' }}>Activity</span>
                            <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>Tasks & work items</p>
                        </div>
                    </div>
                    {/* Gateway */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                            width: '14px',
                            height: '14px',
                            transform: 'rotate(45deg)',
                            background: 'rgba(168, 85, 247, 0.15)',
                            border: '2px solid #a855f7',
                            boxShadow: '0 0 10px rgba(168, 85, 247, 0.4)'
                        }}></div>
                        <div>
                            <span style={{ fontWeight: '600', fontSize: '0.85rem', color: '#e2e8f0' }}>Gateway</span>
                            <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>Decision points</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tree Container with Error Boundary */}
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                transform: `scale(${zoomLevel})`,
                transformOrigin: 'top center',
                transition: 'transform 0.3s ease-out',
                /* Ensure it takes space so scrolling works */
                width: '100%',
                marginTop: '1rem',
                paddingBottom: '4rem'
            }}>
                <ErrorBoundary key={xml ? xml.length : 'empty'}>
                    <TreeNode node={tree} />
                </ErrorBoundary>
            </div>
        </div>
    );
};

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [text, setText] = useState(location.state?.initialText || '');
    const [xml, setXml] = useState('');
    const [accuracy, setAccuracy] = useState(null);
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [viewMode, setViewMode] = useState('diagram'); // 'diagram' | 'text'
    const [processZoom, setProcessZoom] = useState(1);
    const [detectedLanguage, setDetectedLanguage] = useState('en');
    const [engineMode, setEngineMode] = useState('groq'); // groq | rule | hybrid
    const [engineUsed, setEngineUsed] = useState(null);

    // New editing states
    const [normalizedText, setNormalizedText] = useState('');
    const [editedNormalizedText, setEditedNormalizedText] = useState('');
    const [showEditPanel, setShowEditPanel] = useState(false);
    const [regenerating, setRegenerating] = useState(false);

    const containerRef = useRef(null);
    const viewerRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (!user) navigate('/login');
    }, [user, navigate]);

    useEffect(() => {
        if (containerRef.current && !viewerRef.current) {
            viewerRef.current = new BpmnNavigatedViewer({
                container: containerRef.current
            });
        }
    }, []);

    useEffect(() => {
        if (xml && viewerRef.current) {
            viewerRef.current.importXML(xml).then(() => {
                const canvas = viewerRef.current.get('canvas');
                const elementRegistry = viewerRef.current.get('elementRegistry');

                // Adjust viewer background
                // canvas._container.style.backgroundColor = 'var(--bg-canvas)';

                // Add colors to elements
                const elements = elementRegistry.getAll();
                elements.forEach(element => {
                    const type = element.type.toLowerCase();
                    const bo = element.businessObject;

                    // GROUPS
                    if (type.includes('group')) {
                        canvas.addMarker(element.id, 'djs-group');

                        // Check category name for color class
                        if (bo.categoryValueRef && bo.categoryValueRef.value) {
                            const val = bo.categoryValueRef.value.toLowerCase();
                            if (val.includes('user') || val.includes('input')) {
                                canvas.addMarker(element.id, 'group-user-input');
                            } else if (val.includes('success')) {
                                canvas.addMarker(element.id, 'group-success');
                            } else if (val.includes('fail') || val.includes('error')) {
                                canvas.addMarker(element.id, 'group-failure');
                            } else if (val.includes('verify') || val.includes('check')) {
                                canvas.addMarker(element.id, 'group-verification');
                            }
                        }
                    }
                    // TASKS
                    else if (type.includes('task')) {
                        canvas.addMarker(element.id, 'node-task');
                    }
                    // GATEWAYS
                    else if (type.includes('gateway')) {
                        canvas.addMarker(element.id, 'node-gateway');
                    }
                    // START
                    else if (type.includes('startevent')) {
                        canvas.addMarker(element.id, 'node-start');
                    }
                    // END
                    else if (type.includes('endevent')) {
                        canvas.addMarker(element.id, 'node-end');
                    }
                });

                canvas.zoom('fit-viewport');
            }).catch(err => console.error('Error rendering BPMN:', err));
        }
    }, [xml]);

    const handleGenerate = async (forceEnglish = false) => {
        if (!text) return;
        setLoading(true);
        setAccuracy(null);
        setEngineUsed(null);
        if (forceEnglish) {
            // If forcing English, likely we want to reset detectedLanguage view logic or keep it?
            // Usually we just want to see the English version. 
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/generate-bpmn/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, use_rag: !!file, force_english: forceEnglish, mode: engineMode }),
            });
            const data = await response.json();
            if (data.xml) {
                setXml(data.xml);
                setAccuracy(data.accuracy);
                if (data.engine) {
                    setEngineUsed(data.engine);
                }
                if (data.detected_language) {
                    setDetectedLanguage(data.detected_language);
                }
                // Capture normalized text for editing
                if (data.explanation) {
                    setNormalizedText(data.explanation);
                    setEditedNormalizedText(data.explanation);
                }
            }
        } catch (error) {
            console.error("Error generating BPMN:", error);
        } finally {
            setLoading(false);
        }
    };

    // Regenerate diagram from edited normalized text
    const handleRegenerate = async () => {
        if (!editedNormalizedText) return;
        setRegenerating(true);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/generate-bpmn/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Send the edited text directly - it's already normalized
                body: JSON.stringify({ text: editedNormalizedText, use_rag: false, force_english: false, mode: 'rule' }),
            });
            const data = await response.json();
            if (data.xml) {
                setXml(data.xml);
                setAccuracy(data.accuracy);
                // Update the stored normalized text
                setNormalizedText(editedNormalizedText);
                if (data.engine) {
                    setEngineUsed(data.engine + ' (edited)');
                }
            }
        } catch (error) {
            console.error("Error regenerating BPMN:", error);
        } finally {
            setRegenerating(false);
            setShowEditPanel(false);
        }
    };

    const handleFileUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/upload-file/', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setFile(selectedFile);

                // If text was extracted from the file, populate the input field
                if (data.extracted_text && data.extracted_text.trim()) {
                    setText(data.extracted_text);
                    alert(`File processed! Extracted ${data.chunks} chunks. Text content has been loaded into the input field.`);
                } else {
                    alert("File uploaded and processed for RAG context! No text could be extracted directly.");
                }
            } else {
                console.error("Upload error response:", data);
                alert(`Upload failed: ${data.detail || data.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            alert(`Upload failed: ${error.message}`);
        } finally {
            setUploading(false);
        }
    };

    const handleZoom = (delta) => {
        if (viewMode === 'diagram' && viewerRef.current) {
            const canvas = viewerRef.current.get('canvas');
            const currentZoom = canvas.zoom();
            canvas.zoom(currentZoom + delta);
        } else if (viewMode === 'text') {
            setProcessZoom(prev => Math.min(Math.max(prev + delta, 0.2), 3));
        }
    };

    const handleResetZoom = () => {
        if (viewMode === 'diagram' && viewerRef.current) {
            const canvas = viewerRef.current.get('canvas');
            canvas.zoom('fit-viewport');
        } else if (viewMode === 'text') {
            setProcessZoom(1);
        }
    };

    const handleDownloadXml = () => {
        if (!xml) return;
        const blob = new Blob([xml], { type: 'text/xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'process_diagram.bpmn';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div style={{ paddingTop: '80px', height: '100vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Left Panel - Input */}
                <div className="glass" style={{ width: '400px', margin: '1rem', display: 'flex', flexDirection: 'column', borderRadius: '1rem', padding: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <FileText size={20} /> Input Description
                    </h2>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', color: '#cbd5e1', marginBottom: '0.5rem' }}>
                            Engine
                        </label>
                        <select
                            value={engineMode}
                            onChange={(e) => setEngineMode(e.target.value)}
                            style={{ width: '100%', padding: '0.75rem', borderRadius: '0.75rem', background: 'rgba(2, 6, 23, 0.35)', border: '1px solid rgba(148, 163, 184, 0.25)', color: 'white' }}
                        >
                            <option value="groq">Groq</option>
                            <option value="rule">Rule</option>
                            <option value="hybrid">Hybrid (Best by ML score)</option>
                        </select>
                    </div>
                    <textarea
                        style={{ flex: 1, background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', color: 'white', padding: '1rem', resize: 'none', marginBottom: '1rem' }}
                        placeholder="Describe your process..."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />

                    <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
                        <label htmlFor="file-upload" className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', flex: 1, cursor: 'pointer', borderStyle: 'dashed' }}>
                            {uploading ? 'Processing...' : file ? <><Paperclip size={18} /> {file.name.length > 15 ? file.name.substring(0, 15) + '...' : file.name}</> : <><Upload size={18} /> Upload Context (PDF)</>}
                        </label>
                        <input
                            ref={fileInputRef}
                            id="file-upload"
                            type="file"
                            accept=".pdf,.txt,.doc,.docx"
                            onChange={handleFileUpload}
                            style={{ display: 'none' }}
                        />
                        {(file || text || xml) && (
                            <button
                                onClick={() => {
                                    setFile(null);
                                    setText('');
                                    setXml('');
                                    setAccuracy(null);
                                    setNormalizedText('');
                                    setEditedNormalizedText('');
                                    setShowEditPanel(false);
                                    setEngineUsed(null);
                                    // Reset file input value so same file can be uploaded again
                                    if (fileInputRef.current) {
                                        fileInputRef.current.value = '';
                                    }
                                }}
                                className="btn btn-outline"
                                style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem', color: '#f87171', borderColor: '#f87171' }}
                                title="Clear all"
                            >
                                <X size={16} /> Clear
                            </button>
                        )}
                    </div>

                    <button
                        className="btn btn-primary"
                        onClick={() => handleGenerate(false)}
                        disabled={loading}
                        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                    >
                        {loading ? 'Generating...' : <><Send size={18} /> Generate Diagram</>}
                    </button>

                    {accuracy !== null && (
                        <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '0.5rem', border: '1px solid #10b981' }}>
                            <h3 style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: '600', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Activity size={16} /> ML Accuracy Score (XLM-R)
                            </h3>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fff' }}>{accuracy}%</div>
                            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Semantic alignment with generated nodes.</p>
                        </div>
                    )}
                </div>

                {/* Right Panel - Viewer */}
                <div className="glass" style={{ flex: 1, margin: '1rem 1rem 1rem 0', borderRadius: '1rem', position: 'relative', overflow: 'hidden', background: 'rgba(2, 6, 23, 0.35)', display: 'flex', flexDirection: 'column' }}>

                    {/* Toolbar */}
                    <div style={{ padding: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.16)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.55)', backdropFilter: 'blur(12px)' }}>
                        {/* View Toggles */}
                        <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(148, 163, 184, 0.10)', padding: '0.25rem', borderRadius: '0.75rem', border: '1px solid rgba(148, 163, 184, 0.14)' }}>
                            <button
                                onClick={() => setViewMode('diagram')}
                                style={{
                                    display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.5rem 1rem', borderRadius: '0.3rem',
                                    background: viewMode === 'diagram' ? 'rgba(2, 6, 23, 0.55)' : 'transparent',
                                    color: viewMode === 'diagram' ? '#e2e8f0' : '#94a3b8',
                                    fontWeight: viewMode === 'diagram' ? '600' : '400',
                                    boxShadow: viewMode === 'diagram' ? '0 8px 24px rgba(0,0,0,0.25)' : 'none',
                                    border: 'none', cursor: 'pointer'
                                }}
                            >
                                <Map size={18} /> Diagram
                            </button>
                            <button
                                onClick={() => setViewMode('text')}
                                style={{
                                    display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.5rem 1rem', borderRadius: '0.3rem',
                                    background: viewMode === 'text' ? 'rgba(2, 6, 23, 0.55)' : 'transparent',
                                    color: viewMode === 'text' ? '#e2e8f0' : '#94a3b8',
                                    fontWeight: viewMode === 'text' ? '600' : '400',
                                    boxShadow: viewMode === 'text' ? '0 8px 24px rgba(0,0,0,0.25)' : 'none',
                                    border: 'none', cursor: 'pointer'
                                }}
                            >
                                <List size={18} /> Process Flow
                            </button>
                        </div>

                        {/* Actions */}
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {engineUsed && (
                                <div style={{ display: 'flex', alignItems: 'center', padding: '0.4rem 0.75rem', borderRadius: '999px', border: '1px solid rgba(148, 163, 184, 0.22)', background: 'rgba(2, 6, 23, 0.35)', color: '#e2e8f0', fontSize: '0.8rem', fontWeight: '600' }}>
                                    Engine: {engineUsed}
                                </div>
                            )}
                            {xml && detectedLanguage !== 'en' && (
                                <button
                                    onClick={() => handleGenerate(true)}
                                    style={{
                                        display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.5rem 1rem', borderRadius: '0.3rem',
                                        background: '#3b82f6', color: 'white', fontWeight: '600',
                                        border: 'none', cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                                    }}
                                >
                                    Generate in English
                                </button>
                            )}

                            <>
                                <button
                                    onClick={() => handleZoom(0.2)}
                                    style={{ padding: '0.5rem', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.22)', background: 'rgba(2, 6, 23, 0.35)', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    title="Zoom In"
                                >
                                    <ZoomIn size={18} />
                                </button>
                                <button
                                    onClick={() => handleZoom(-0.2)}
                                    style={{ padding: '0.5rem', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.22)', background: 'rgba(2, 6, 23, 0.35)', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    title="Zoom Out"
                                >
                                    <ZoomOut size={18} />
                                </button>
                                <button
                                    onClick={handleResetZoom}
                                    style={{ padding: '0.5rem', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.22)', background: 'rgba(2, 6, 23, 0.35)', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    title="Reset View"
                                >
                                    <RotateCcw size={18} />
                                </button>
                            </>
                            <button
                                onClick={handleDownloadXml}
                                style={{ padding: '0.5rem', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.22)', background: 'rgba(2, 6, 23, 0.35)', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                title="Download BPMN"
                            >
                                <Download size={18} />
                            </button>
                            {/* Edit Button */}
                            {normalizedText && (
                                <button
                                    onClick={() => {
                                        setShowEditPanel(!showEditPanel);
                                        setEditedNormalizedText(normalizedText);
                                    }}
                                    style={{
                                        padding: '0.5rem',
                                        borderRadius: '0.6rem',
                                        border: showEditPanel ? '1px solid #a855f7' : '1px solid rgba(148, 163, 184, 0.22)',
                                        background: showEditPanel ? 'rgba(168, 85, 247, 0.2)' : 'rgba(2, 6, 23, 0.35)',
                                        color: showEditPanel ? '#a855f7' : '#cbd5e1',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}
                                    title="Edit Diagram Text"
                                >
                                    <Edit2 size={18} />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Collapsible Edit Panel */}
                    {showEditPanel && (
                        <div style={{
                            padding: '1rem',
                            borderBottom: '1px solid rgba(148, 163, 184, 0.16)',
                            background: 'rgba(168, 85, 247, 0.05)',
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                                <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: '#a855f7', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Edit2 size={16} /> Edit Process Flow Text
                                </h4>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button
                                        onClick={handleRegenerate}
                                        disabled={regenerating}
                                        style={{
                                            padding: '0.4rem 1rem',
                                            borderRadius: '0.5rem',
                                            border: 'none',
                                            background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)',
                                            color: 'white',
                                            fontWeight: '600',
                                            fontSize: '0.85rem',
                                            cursor: regenerating ? 'wait' : 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.5rem'
                                        }}
                                    >
                                        {regenerating ? <><RefreshCw size={14} className="animate-spin" /> Regenerating...</> : <><RefreshCw size={14} /> Regenerate Diagram</>}
                                    </button>
                                    <button
                                        onClick={() => setShowEditPanel(false)}
                                        style={{
                                            padding: '0.4rem',
                                            borderRadius: '0.5rem',
                                            border: '1px solid rgba(148, 163, 184, 0.22)',
                                            background: 'transparent',
                                            color: '#94a3b8',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                            </div>
                            <textarea
                                value={editedNormalizedText}
                                onChange={(e) => setEditedNormalizedText(e.target.value)}
                                style={{
                                    width: '100%',
                                    minHeight: '200px',
                                    padding: '1rem',
                                    borderRadius: '0.5rem',
                                    border: '1px solid rgba(168, 85, 247, 0.3)',
                                    background: 'rgba(2, 6, 23, 0.6)',
                                    color: '#e2e8f0',
                                    fontFamily: 'monospace',
                                    fontSize: '0.9rem',
                                    lineHeight: '1.5',
                                    resize: 'vertical'
                                }}
                                placeholder="Edit the normalized process flow text..."
                            />
                            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                                Tip: Use "Start Process", "End Process", "If/Else/End If" to structure your flow. Click "Regenerate Diagram" to apply changes.
                            </p>
                        </div>
                    )}

                    <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                        <div
                            ref={containerRef}
                            style={{
                                width: '100%',
                                height: '100%',
                                display: viewMode === 'diagram' ? 'block' : 'none',
                                visibility: !xml ? 'hidden' : 'visible' // Hide canvas when no XML to show placeholders
                            }}
                        ></div>

                        {viewMode === 'text' && (
                            xml ? <ErrorBoundary><ProcessFlowRenderer xml={xml} zoomLevel={processZoom} /></ErrorBoundary> : null
                        )}

                        {!xml && (
                            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: '#64748b', textAlign: 'center' }}>
                                <p style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>Ready to generate</p>
                                <p style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Enter your process description and click generate</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Simple Error Boundary Component
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ProcessFlowRenderer Boundary Error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '1rem', background: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '0.5rem', marginTop: '1rem' }}>
                    <b>Something went wrong rendering the flow.</b>
                    <br />
                    <small>{this.state.error && this.state.error.toString()}</small>
                </div>
            );
        }

        return this.props.children;
    }
}

export default Dashboard;
